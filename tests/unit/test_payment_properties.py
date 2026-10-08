"""Property-based tests: invariants that must hold for any sequence of refunds.

Example-based tests check the cases we thought of. These check the rule itself
against hundreds of generated request sequences, including retries.
"""

from datetime import UTC, datetime
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from service_template.domain.errors import DomainError
from service_template.domain.money import Currency, Money
from service_template.domain.payment import Payment, PaymentId, Refund, RefundId

REQUESTED_AT = datetime(2026, 1, 15, 9, 30, tzinfo=UTC)

paise = st.integers(min_value=0, max_value=20_000)
captured_amounts = st.integers(min_value=1, max_value=20_000)
# Few distinct keys, so that generated sequences contain retries and conflicts.
idempotency_keys = st.sampled_from(["key-a", "key-b", "key-c", "key-d", "key-e"])
refund_requests = st.lists(st.tuples(paise, idempotency_keys), max_size=12)


def inr_from_paise(minor_units: int) -> Money:
    return Money(Decimal(minor_units) / 100, Currency.INR)


def try_refund(payment: Payment, minor_units: int, key: str) -> Refund | None:
    try:
        return payment.request_refund(
            refund_id=RefundId(f"rf_{len(payment.refunds) + 1}"),
            amount=inr_from_paise(minor_units),
            reason=None,
            idempotency_key=key,
            requested_at=REQUESTED_AT,
        )
    except DomainError:
        return None


@given(captured=captured_amounts, requests=refund_requests)
def test_refunds_never_exceed_the_captured_amount(
    captured: int, requests: list[tuple[int, str]]
) -> None:
    payment = Payment(id=PaymentId("pay_1"), captured=inr_from_paise(captured))

    for minor_units, key in requests:
        try_refund(payment, minor_units, key)

        assert payment.refunded.amount <= payment.captured.amount
        assert payment.refunded + payment.refundable == payment.captured


@given(captured=captured_amounts, requests=refund_requests)
def test_retrying_accepted_requests_changes_nothing(
    captured: int, requests: list[tuple[int, str]]
) -> None:
    payment = Payment(id=PaymentId("pay_1"), captured=inr_from_paise(captured))
    accepted = [
        (minor_units, key, refund)
        for minor_units, key in requests
        if (refund := try_refund(payment, minor_units, key)) is not None
    ]
    refunds_before = list(payment.refunds)

    for minor_units, key, original in accepted:
        assert try_refund(payment, minor_units, key) == original

    assert payment.refunds == refunds_before


@given(captured=captured_amounts, requests=refund_requests)
def test_every_idempotency_key_is_recorded_at_most_once(
    captured: int, requests: list[tuple[int, str]]
) -> None:
    payment = Payment(id=PaymentId("pay_1"), captured=inr_from_paise(captured))

    for minor_units, key in requests:
        try_refund(payment, minor_units, key)

    keys = [refund.idempotency_key for refund in payment.refunds]
    assert len(keys) == len(set(keys))
