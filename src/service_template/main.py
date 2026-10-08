"""Composition root: the one place where the layers are wired together.

Run with:  uvicorn --factory service_template.main:create_app
"""

from fastapi import FastAPI

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.adapters.system import new_refund_id, utc_now
from service_template.api import health, refunds
from service_template.api.errors import register_error_handlers
from service_template.application.ports import PaymentRepository
from service_template.application.request_refund import RequestRefund

API_VERSION = "1.0.0"


def create_app(payments: PaymentRepository | None = None) -> FastAPI:
    """Build the application.

    Pass adapters to override the defaults; the tests do this to control the
    data the service starts with.
    """
    if payments is None:
        payments = InMemoryPaymentRepository()

    app = FastAPI(
        title="Service Template",
        version=API_VERSION,
        description="Example service: refunds against captured payments.",
    )
    app.state.request_refund = RequestRefund(
        payments=payments,
        clock=utc_now,
        new_refund_id=new_refund_id,
    )

    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(refunds.router)
    return app
