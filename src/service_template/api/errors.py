"""Turns exceptions into HTTP error responses.

Every error leaves the service as an `ErrorResponse`, whatever caused it.
"""

from collections.abc import Awaitable, Callable, Mapping

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from service_template.api.schemas import ErrorCode, ErrorDetail, ErrorResponse
from service_template.application.request_refund import PaymentNotFoundError
from service_template.domain.errors import (
    CurrencyMismatchError,
    IdempotencyKeyConflictError,
    InvalidAmountError,
    RefundExceedsRefundableAmountError,
)

_Handler = Callable[[Request, Exception], Awaitable[JSONResponse]]

_KNOWN_ERRORS: dict[type[Exception], tuple[int, ErrorCode]] = {
    PaymentNotFoundError: (404, ErrorCode.PAYMENT_NOT_FOUND),
    IdempotencyKeyConflictError: (409, ErrorCode.IDEMPOTENCY_KEY_CONFLICT),
    CurrencyMismatchError: (422, ErrorCode.CURRENCY_MISMATCH),
    InvalidAmountError: (422, ErrorCode.INVALID_AMOUNT),
    RefundExceedsRefundableAmountError: (422, ErrorCode.REFUND_EXCEEDS_REFUNDABLE_AMOUNT),
}

_FRAMEWORK_ERRORS: dict[int, ErrorCode] = {
    400: ErrorCode.BAD_REQUEST,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.METHOD_NOT_ALLOWED,
}

_INTERNAL_ERROR = ErrorResponse(code=ErrorCode.INTERNAL_ERROR, message="internal server error")


def register_error_handlers(app: FastAPI) -> None:
    for error_type, (status_code, code) in _KNOWN_ERRORS.items():
        app.add_exception_handler(error_type, _known_error(status_code, code))
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(HTTPException, _framework_error)
    app.add_exception_handler(Exception, _unexpected_error)


def _known_error(status_code: int, code: ErrorCode) -> _Handler:
    async def handle(_request: Request, error: Exception) -> JSONResponse:
        return _respond(status_code, ErrorResponse(code=code, message=str(error)))

    return handle


async def _validation_error(_request: Request, error: Exception) -> JSONResponse:
    # Report where each problem is and what the rule is, but never echo the
    # rejected input back: it may contain data that must not end up in logs.
    problems = error.errors() if isinstance(error, RequestValidationError) else []
    details = [
        ErrorDetail(
            field=".".join(str(part) for part in problem["loc"]),
            message=problem["msg"],
        )
        for problem in problems
    ]
    body = ErrorResponse(
        code=ErrorCode.VALIDATION_ERROR,
        message="the request is not valid",
        details=details,
    )
    return _respond(422, body)


async def _framework_error(_request: Request, error: Exception) -> JSONResponse:
    # Errors raised by the framework itself: unknown route, wrong method,
    # a body that cannot be decoded. Headers such as Allow are passed through.
    if not isinstance(error, HTTPException):
        return _respond(500, _INTERNAL_ERROR)
    code = _FRAMEWORK_ERRORS.get(error.status_code, ErrorCode.BAD_REQUEST)
    body = ErrorResponse(code=code, message=str(error.detail))
    return _respond(error.status_code, body, headers=error.headers)


async def _unexpected_error(_request: Request, _error: Exception) -> JSONResponse:
    # The exception is re-raised by the server after this response is sent,
    # so it is still logged with its traceback. Clients get no internals.
    return _respond(500, _INTERNAL_ERROR)


def _respond(
    status_code: int,
    body: ErrorResponse,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(mode="json"),
        headers=headers,
    )
