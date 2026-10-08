"""Refund endpoints (spec 0001)."""

from typing import Annotated, Any

from fastapi import APIRouter, Header, Path

from service_template.api.dependencies import RequestRefundUseCase
from service_template.api.schemas import ErrorResponse, RefundRequest, RefundResponse
from service_template.application.request_refund import RequestRefundCommand
from service_template.domain.payment import PaymentId

router = APIRouter(prefix="/v1", tags=["refunds"])

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9_-]+$"

PaymentIdPath = Annotated[
    str,
    Path(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN, examples=["pay_8Zk2"]),
]
IdempotencyKeyHeader = Annotated[
    str,
    Header(
        min_length=1,
        max_length=255,
        pattern=_IDENTIFIER_PATTERN,
        description=(
            "Unique key for this refund request. Retrying with the same key and "
            "the same body returns the original refund instead of creating another."
        ),
        examples=["3f1c9a52-7d0e-4c58-9d55-0f2d6b7a1e11"],
    ),
]

_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": ErrorResponse, "description": "The request body could not be read."},
    404: {"model": ErrorResponse, "description": "The payment does not exist."},
    409: {
        "model": ErrorResponse,
        "description": "The idempotency key was already used for a different request.",
    },
    422: {
        "model": ErrorResponse,
        "description": "The request is malformed or breaks a business rule.",
    },
}


@router.post(
    "/payments/{payment_id}/refunds",
    operation_id="requestRefund",
    summary="Refund part or all of a captured payment",
    status_code=201,
    responses=_ERROR_RESPONSES,
)
def request_refund(
    payment_id: PaymentIdPath,
    body: RefundRequest,
    idempotency_key: IdempotencyKeyHeader,
    use_case: RequestRefundUseCase,
) -> RefundResponse:
    command = RequestRefundCommand(
        payment_id=PaymentId(payment_id),
        amount=body.amount.to_domain(),
        reason=body.reason,
        idempotency_key=idempotency_key,
    )
    refund = use_case.execute(command)
    return RefundResponse.from_domain(command.payment_id, refund)
