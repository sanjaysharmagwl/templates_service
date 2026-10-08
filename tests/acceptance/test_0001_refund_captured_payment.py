"""Acceptance tests for spec 0001: refund a captured payment.

Each acceptance criterion in specs/0001-refund-captured-payment/spec.md has at
least one test here, marked with `covers`. The tests talk to the service over
HTTP, exactly as a client would.

Given, for every test: payment `pay_1` was captured for 100.00 INR.
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.domain.payment import Payment, PaymentId
from tests.factories import captured_payment, inr

PAYMENT_ID = PaymentId("pay_1")
REFUNDS_URL = f"/v1/payments/{PAYMENT_ID}/refunds"


@pytest.fixture(autouse=True)
def payment_of_100_inr(payments: InMemoryPaymentRepository) -> None:
    payments.save(captured_payment(PAYMENT_ID, inr("100.00")))


def request_refund(
    client: TestClient,
    value: str,
    *,
    currency: str = "INR",
    key: str = "key-1",
    reason: str | None = None,
) -> Response:
    body: dict[str, object] = {"amount": {"value": value, "currency": currency}}
    if reason is not None:
        body["reason"] = reason
    return client.post(REFUNDS_URL, headers={"Idempotency-Key": key}, json=body)


def stored_payment(payments: InMemoryPaymentRepository) -> Payment:
    payment = payments.get(PAYMENT_ID)
    assert payment is not None
    return payment


@pytest.mark.covers("0001:AC-1")
def test_partial_refund_is_recorded(
    client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    response = request_refund(client, "30.00", reason="Customer returned the item")

    assert response.status_code == 201
    refund = response.json()
    assert refund["id"]
    assert refund["payment_id"] == PAYMENT_ID
    assert refund["amount"] == {"value": "30.00", "currency": "INR"}
    assert refund["reason"] == "Customer returned the item"
    assert refund["requested_at"]
    assert stored_payment(payments).refundable.amount == Decimal("70.00")


@pytest.mark.covers("0001:AC-2")
def test_payment_can_be_refunded_in_parts_up_to_the_captured_amount(
    client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    first = request_refund(client, "30.00", key="key-1")
    second = request_refund(client, "70.00", key="key-2")

    assert first.status_code == 201
    assert second.status_code == 201
    assert stored_payment(payments).refundable.is_zero


@pytest.mark.covers("0001:AC-3")
def test_refund_larger_than_the_refundable_amount_is_rejected(
    client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    request_refund(client, "30.00", key="key-1")

    response = request_refund(client, "70.01", key="key-2")

    assert response.status_code == 422
    assert response.json()["code"] == "refund_exceeds_refundable_amount"
    assert stored_payment(payments).refundable.amount == Decimal("70.00")


@pytest.mark.covers("0001:AC-4")
def test_refund_in_another_currency_is_rejected(
    client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    response = request_refund(client, "30.00", currency="USD")

    assert response.status_code == 422
    assert response.json()["code"] == "currency_mismatch"
    assert stored_payment(payments).refunds == []


@pytest.mark.covers("0001:AC-5")
@pytest.mark.parametrize(
    ("value", "why"),
    [
        ("0.00", "a refund must move some money"),
        ("0", "a refund must move some money"),
        ("10.005", "INR has two decimal places"),
    ],
)
def test_amount_that_is_not_valid_for_the_currency_is_rejected(
    client: TestClient, payments: InMemoryPaymentRepository, value: str, why: str
) -> None:
    response = request_refund(client, value)

    assert response.status_code == 422, why
    assert response.json()["code"] == "invalid_amount"
    assert stored_payment(payments).refunds == []


@pytest.mark.covers("0001:AC-6")
def test_retried_request_returns_the_original_refund(
    client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    original = request_refund(client, "30.00", key="key-1", reason="Duplicate charge")

    retry = request_refund(client, "30.00", key="key-1", reason="Duplicate charge")

    assert retry.status_code == 201
    assert retry.json() == original.json()
    assert len(stored_payment(payments).refunds) == 1


@pytest.mark.covers("0001:AC-7")
@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("40.00", "Duplicate charge"),
        ("30.00", "Goodwill"),
    ],
    ids=["different amount", "different reason"],
)
def test_reusing_a_key_for_a_different_request_is_rejected(
    client: TestClient, payments: InMemoryPaymentRepository, value: str, reason: str
) -> None:
    request_refund(client, "30.00", key="key-1", reason="Duplicate charge")

    response = request_refund(client, value, key="key-1", reason=reason)

    assert response.status_code == 409
    assert response.json()["code"] == "idempotency_key_conflict"
    assert len(stored_payment(payments).refunds) == 1


@pytest.mark.covers("0001:AC-8")
def test_refund_on_an_unknown_payment_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/v1/payments/pay_unknown/refunds",
        headers={"Idempotency-Key": "key-1"},
        json={"amount": {"value": "30.00", "currency": "INR"}},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "payment_not_found"


@pytest.mark.covers("0001:AC-9")
def test_request_without_an_idempotency_key_is_rejected(client: TestClient) -> None:
    response = client.post(
        REFUNDS_URL,
        json={"amount": {"value": "30.00", "currency": "INR"}},
    )

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert error["details"] == [{"field": "header.idempotency-key", "message": "Field required"}]


@pytest.mark.covers("0001:AC-9")
@pytest.mark.parametrize(
    "body",
    [
        {"amount": {"value": 30.0, "currency": "INR"}},
        {"amount": {"value": "-30.00", "currency": "INR"}},
        {"amount": {"value": "30.00", "currency": "XXX"}},
        {"amount": {"value": "30.00", "currency": "INR"}, "unexpected": "field"},
        {"amount": {"value": "30.00", "currency": "INR"}, "reason": ""},
        {},
    ],
    ids=[
        "amount as a JSON number",
        "negative amount",
        "unsupported currency",
        "unknown field",
        "empty reason",
        "empty body",
    ],
)
def test_malformed_request_is_rejected(
    client: TestClient, payments: InMemoryPaymentRepository, body: dict[str, object]
) -> None:
    response = client.post(
        REFUNDS_URL,
        headers={"Idempotency-Key": "key-1"},
        json=body,
    )

    assert response.status_code == 422
    error = response.json()
    assert error["code"] == "validation_error"
    assert error["details"], "each problem should be reported with its location"
    assert stored_payment(payments).refunds == []


@pytest.mark.covers("0001:AC-9")
def test_validation_errors_do_not_echo_the_rejected_input(client: TestClient) -> None:
    response = client.post(
        REFUNDS_URL,
        headers={"Idempotency-Key": "key-1"},
        json={"amount": {"value": "4111111111111111-not-an-amount", "currency": "INR"}},
    )

    assert response.status_code == 422
    assert "4111111111111111" not in response.text
