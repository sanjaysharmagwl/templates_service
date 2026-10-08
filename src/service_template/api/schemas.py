"""Request and response bodies.

These models define the wire contract: contracts/openapi.json is generated
from them. Change them only as part of a spec, then run `make openapi`.
"""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from service_template.domain.money import Currency, Money
from service_template.domain.payment import PaymentId, Refund

AMOUNT_PATTERN = r"^\d{1,12}(\.\d{1,3})?$"


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Amount(ApiModel):
    """A sum of money. The value is a decimal string, never a JSON number."""

    value: str = Field(
        pattern=AMOUNT_PATTERN,
        description="Amount in major units of the currency, for example 25.00.",
        examples=["25.00"],
    )
    currency: Currency

    def to_domain(self) -> Money:
        return Money(Decimal(self.value), self.currency)

    @classmethod
    def from_domain(cls, money: Money) -> Amount:
        return cls(value=format(money.amount, "f"), currency=money.currency)


class RefundRequest(ApiModel):
    amount: Amount
    reason: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Why the refund is being made. Shown to operations staff.",
        examples=["Customer returned the item"],
    )


class RefundResponse(ApiModel):
    id: str
    payment_id: str
    amount: Amount
    reason: str | None
    requested_at: AwareDatetime

    @classmethod
    def from_domain(cls, payment_id: PaymentId, refund: Refund) -> RefundResponse:
        return cls(
            id=refund.id,
            payment_id=payment_id,
            amount=Amount.from_domain(refund.amount),
            reason=refund.reason,
            requested_at=refund.requested_at,
        )


class HealthResponse(ApiModel):
    status: Literal["ok"]


class ErrorCode(StrEnum):
    """Stable, machine-readable error codes. Clients branch on these."""

    BAD_REQUEST = "bad_request"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    VALIDATION_ERROR = "validation_error"
    PAYMENT_NOT_FOUND = "payment_not_found"
    IDEMPOTENCY_KEY_CONFLICT = "idempotency_key_conflict"
    CURRENCY_MISMATCH = "currency_mismatch"
    INVALID_AMOUNT = "invalid_amount"
    REFUND_EXCEEDS_REFUNDABLE_AMOUNT = "refund_exceeds_refundable_amount"
    INTERNAL_ERROR = "internal_error"


class ErrorDetail(ApiModel):
    field: str = Field(description="Location of the problem, for example body.amount.value.")
    message: str


class ErrorResponse(ApiModel):
    """The body of every error response from this service."""

    code: ErrorCode
    message: str = Field(description="Human-readable explanation. Do not parse it.")
    details: list[ErrorDetail] = Field(default_factory=list)
