"""Unit tests for the RequestRefund use case: orchestration, not business rules."""

from datetime import UTC, datetime

import pytest

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.application.request_refund import (
    PaymentNotFoundError,
    RequestRefund,
    RequestRefundCommand,
)
from service_template.domain.errors import RefundExceedsRefundableAmountError
from service_template.domain.payment import PaymentId, RefundId
from tests.factories import captured_payment, inr

NOW = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)
PAYMENT_ID = PaymentId("pay_1")


@pytest.fixture
def request_refund(payments: InMemoryPaymentRepository) -> RequestRefund:
    payments.save(captured_payment(PAYMENT_ID, inr("100.00")))
    return RequestRefund(
        payments=payments,
        clock=lambda: NOW,
        new_refund_id=lambda: RefundId("rf_fixed"),
    )


def command(value: str, payment_id: PaymentId = PAYMENT_ID) -> RequestRefundCommand:
    return RequestRefundCommand(
        payment_id=payment_id,
        amount=inr(value),
        reason=None,
        idempotency_key="key-1",
    )


def test_accepted_refund_is_stored_with_its_id_and_time(
    request_refund: RequestRefund, payments: InMemoryPaymentRepository
) -> None:
    refund = request_refund.execute(command("30.00"))

    assert refund.id == "rf_fixed"
    assert refund.requested_at == NOW
    stored = payments.get(PAYMENT_ID)
    assert stored is not None
    assert stored.refunds == [refund]


def test_rejected_refund_is_not_stored(
    request_refund: RequestRefund, payments: InMemoryPaymentRepository
) -> None:
    with pytest.raises(RefundExceedsRefundableAmountError):
        request_refund.execute(command("100.01"))

    stored = payments.get(PAYMENT_ID)
    assert stored is not None
    assert stored.refunds == []


@pytest.mark.covers("0001:AC-8")
def test_unknown_payment_is_reported(request_refund: RequestRefund) -> None:
    with pytest.raises(PaymentNotFoundError, match="pay_missing") as raised:
        request_refund.execute(command("30.00", payment_id=PaymentId("pay_missing")))

    assert raised.value.payment_id == "pay_missing"
