"""Unit tests for the refund rules on the Payment aggregate (spec 0001)."""

from datetime import UTC, datetime

import pytest

from service_template.domain.errors import (
    CurrencyMismatchError,
    IdempotencyKeyConflictError,
    InvalidAmountError,
    RefundExceedsRefundableAmountError,
)
from service_template.domain.money import Money
from service_template.domain.payment import Payment, Refund, RefundId
from tests.factories import captured_payment, inr, usd

REQUESTED_AT = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)


@pytest.fixture
def payment() -> Payment:
    return captured_payment("pay_1", inr("100.00"))


def refund(
    payment: Payment,
    amount: Money,
    *,
    key: str = "key-1",
    reason: str | None = None,
    refund_id: str = "rf_1",
) -> Refund:
    return payment.request_refund(
        refund_id=RefundId(refund_id),
        amount=amount,
        reason=reason,
        idempotency_key=key,
        requested_at=REQUESTED_AT,
    )


def test_new_payment_is_fully_refundable(payment: Payment) -> None:
    assert payment.refunded == inr("0")
    assert payment.refundable == inr("100.00")


@pytest.mark.covers("0001:AC-1")
def test_refund_reduces_the_refundable_amount(payment: Payment) -> None:
    recorded = refund(payment, inr("30.00"), reason="Customer returned the item")

    assert recorded == Refund(
        id=RefundId("rf_1"),
        amount=inr("30.00"),
        reason="Customer returned the item",
        idempotency_key="key-1",
        requested_at=REQUESTED_AT,
    )
    assert payment.refunded == inr("30.00")
    assert payment.refundable == inr("70.00")


@pytest.mark.covers("0001:AC-2")
def test_the_whole_captured_amount_can_be_refunded(payment: Payment) -> None:
    refund(payment, inr("30.00"), key="key-1")
    refund(payment, inr("70.00"), key="key-2")

    assert payment.refundable.is_zero


@pytest.mark.covers("0001:AC-3")
def test_refund_above_the_refundable_amount_is_rejected(payment: Payment) -> None:
    refund(payment, inr("30.00"), key="key-1")

    with pytest.raises(RefundExceedsRefundableAmountError, match=r"70\.00 INR"):
        refund(payment, inr("70.01"), key="key-2")

    assert payment.refunded == inr("30.00")


@pytest.mark.covers("0001:AC-4")
def test_refund_in_another_currency_is_rejected(payment: Payment) -> None:
    with pytest.raises(CurrencyMismatchError, match="captured in INR"):
        refund(payment, usd("30.00"))

    assert payment.refunds == []


@pytest.mark.covers("0001:AC-5")
def test_refund_of_nothing_is_rejected(payment: Payment) -> None:
    with pytest.raises(InvalidAmountError, match="greater than zero"):
        refund(payment, inr("0.00"))


@pytest.mark.covers("0001:AC-6")
def test_repeated_request_returns_the_original_refund(payment: Payment) -> None:
    original = refund(payment, inr("30.00"), key="key-1", refund_id="rf_1")

    repeated = refund(payment, inr("30.00"), key="key-1", refund_id="rf_2")

    assert repeated is original
    assert payment.refunds == [original]


@pytest.mark.covers("0001:AC-6")
def test_repeated_request_succeeds_even_when_nothing_is_left_to_refund(payment: Payment) -> None:
    original = refund(payment, inr("100.00"), key="key-1")

    assert refund(payment, inr("100.00"), key="key-1") is original


@pytest.mark.covers("0001:AC-7")
@pytest.mark.parametrize(
    ("amount", "reason"),
    [
        (inr("40.00"), "Duplicate charge"),
        (inr("30.00"), "Goodwill"),
        (usd("30.00"), "Duplicate charge"),
    ],
    ids=["different amount", "different reason", "different currency"],
)
def test_key_reused_for_a_different_request_is_rejected(
    payment: Payment, amount: Money, reason: str
) -> None:
    refund(payment, inr("30.00"), key="key-1", reason="Duplicate charge")

    with pytest.raises(IdempotencyKeyConflictError):
        refund(payment, amount, key="key-1", reason=reason)

    assert payment.refunded == inr("30.00")
