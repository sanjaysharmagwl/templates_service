"""Use case: refund part or all of a captured payment (spec 0001)."""

from dataclasses import dataclass

from service_template.application.ports import Clock, PaymentRepository, RefundIdFactory
from service_template.domain.money import Money
from service_template.domain.payment import PaymentId, Refund


class PaymentNotFoundError(Exception):
    """No payment exists with the requested identifier."""

    def __init__(self, payment_id: PaymentId) -> None:
        super().__init__(f"payment {payment_id} was not found")
        self.payment_id = payment_id


@dataclass(frozen=True, slots=True)
class RequestRefundCommand:
    payment_id: PaymentId
    amount: Money
    reason: str | None
    idempotency_key: str


class RequestRefund:
    def __init__(
        self,
        payments: PaymentRepository,
        clock: Clock,
        new_refund_id: RefundIdFactory,
    ) -> None:
        self._payments = payments
        self._clock = clock
        self._new_refund_id = new_refund_id

    def execute(self, command: RequestRefundCommand) -> Refund:
        payment = self._payments.get(command.payment_id)
        if payment is None:
            raise PaymentNotFoundError(command.payment_id)

        refund = payment.request_refund(
            refund_id=self._new_refund_id(),
            amount=command.amount,
            reason=command.reason,
            idempotency_key=command.idempotency_key,
            requested_at=self._clock(),
        )
        self._payments.save(payment)
        return refund
