"""The Payment aggregate and the refunds issued against it.

Implements the rules in specs/0001-refund-captured-payment/spec.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType

from service_template.domain.errors import (
    CurrencyMismatchError,
    IdempotencyKeyConflictError,
    InvalidAmountError,
    RefundExceedsRefundableAmountError,
)
from service_template.domain.money import Money

PaymentId = NewType("PaymentId", str)
RefundId = NewType("RefundId", str)


@dataclass(frozen=True, slots=True)
class Refund:
    """Money returned to the payer from one payment."""

    id: RefundId
    amount: Money
    reason: str | None
    idempotency_key: str
    requested_at: datetime


@dataclass(slots=True)
class Payment:
    """A captured payment.

    Invariant: the refunds on a payment never add up to more than was captured.
    All refunds go through `request_refund`, which is what protects it.
    """

    id: PaymentId
    captured: Money
    refunds: list[Refund] = field(default_factory=list)

    @property
    def refunded(self) -> Money:
        total = Money.zero(self.captured.currency)
        for refund in self.refunds:
            total += refund.amount
        return total

    @property
    def refundable(self) -> Money:
        return self.captured - self.refunded

    def request_refund(
        self,
        *,
        refund_id: RefundId,
        amount: Money,
        reason: str | None,
        idempotency_key: str,
        requested_at: datetime,
    ) -> Refund:
        """Record a refund, or return the one already recorded for this key.

        A repeated request (same key, same amount and reason) returns the
        original refund and changes nothing, so clients can retry safely.
        """
        previous = self._refund_with_key(idempotency_key)
        if previous is not None:
            if (previous.amount, previous.reason) != (amount, reason):
                raise IdempotencyKeyConflictError(
                    "this idempotency key was already used for a different refund request"
                )
            return previous

        if amount.currency != self.captured.currency:
            raise CurrencyMismatchError(
                f"payment was captured in {self.captured.currency}, "
                f"refund requested in {amount.currency}"
            )
        if amount.is_zero:
            raise InvalidAmountError("refund amount must be greater than zero")
        if amount.amount > self.refundable.amount:
            raise RefundExceedsRefundableAmountError(
                f"refund of {amount} exceeds the refundable amount of {self.refundable}"
            )

        refund = Refund(
            id=refund_id,
            amount=amount,
            reason=reason,
            idempotency_key=idempotency_key,
            requested_at=requested_at,
        )
        self.refunds.append(refund)
        return refund

    def _refund_with_key(self, idempotency_key: str) -> Refund | None:
        for refund in self.refunds:
            if refund.idempotency_key == idempotency_key:
                return refund
        return None
