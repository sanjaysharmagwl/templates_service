"""FastAPI dependencies that hand use cases to the routes.

The use cases are built once in `main.create_app` and stored on `app.state`.
"""

from typing import Annotated

from fastapi import Depends, Request

from service_template.application.request_refund import RequestRefund


def _request_refund(request: Request) -> RequestRefund:
    use_case: RequestRefund = request.app.state.request_refund
    return use_case


RequestRefundUseCase = Annotated[RequestRefund, Depends(_request_refund)]
