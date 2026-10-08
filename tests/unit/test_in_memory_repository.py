"""The in-memory repository must behave like a database, or tests built on it lie."""

from datetime import UTC, datetime

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.domain.payment import PaymentId, RefundId
from tests.factories import captured_payment, inr

PAYMENT_ID = PaymentId("pay_1")


def test_unknown_payment_is_none(payments: InMemoryPaymentRepository) -> None:
    assert payments.get(PAYMENT_ID) is None


def test_saved_payment_can_be_loaded(payments: InMemoryPaymentRepository) -> None:
    payment = captured_payment(PAYMENT_ID, inr("100.00"))

    payments.save(payment)

    assert payments.get(PAYMENT_ID) == payment


def test_changes_are_not_stored_until_saved(payments: InMemoryPaymentRepository) -> None:
    payments.save(captured_payment(PAYMENT_ID, inr("100.00")))
    loaded = payments.get(PAYMENT_ID)
    assert loaded is not None

    loaded.request_refund(
        refund_id=RefundId("rf_1"),
        amount=inr("30.00"),
        reason=None,
        idempotency_key="key-1",
        requested_at=datetime(2026, 1, 15, 9, 30, tzinfo=UTC),
    )

    reloaded = payments.get(PAYMENT_ID)
    assert reloaded is not None
    assert reloaded.refunds == []
