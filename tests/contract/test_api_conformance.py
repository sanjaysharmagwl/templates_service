"""Fuzz the API against its own OpenAPI document.

Schemathesis generates requests for every operation and checks that each
response is one the contract allows: a documented status code, the documented
content type, a body matching the documented schema, and never a server error.
"""

from typing import Any

import schemathesis
from fastapi import FastAPI
from hypothesis import settings
from schemathesis.config import SchemathesisConfig

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.main import create_app
from tests.factories import captured_payment, inr

ApiCase = schemathesis.Case[Any]

EXISTING_PAYMENT_ID = "pay_contract"

# A request can satisfy the JSON schema and still break a business rule the
# schema cannot express (for example, 25.50 is not a valid amount of JPY).
# Those are answered with 422, so 422 is an acceptable reply to valid input.
ACCEPT_BUSINESS_RULE_REJECTIONS = {
    "positive_data_acceptance": {"expected-statuses": ["2xx", 404, 409, 422]},
}


def _app_with_one_payment() -> FastAPI:
    payments = InMemoryPaymentRepository()
    payments.save(captured_payment(EXISTING_PAYMENT_ID, inr("1000000.00")))
    return create_app(payments)


def _load_schema(**extra_config: object) -> schemathesis.BaseSchema:
    config = SchemathesisConfig.from_dict(
        {"checks": ACCEPT_BUSINESS_RULE_REJECTIONS, **extra_config}
    )
    return schemathesis.openapi.from_asgi("/openapi.json", _app_with_one_payment(), config=config)


any_request = _load_schema()
valid_requests_only = _load_schema(generation={"mode": "positive"})


@any_request.parametrize()
@settings(max_examples=100, deadline=None)
def test_every_response_is_allowed_by_the_contract(case: ApiCase) -> None:
    """Valid and invalid requests alike: mostly exercises the error paths."""
    case.call_and_validate()


@valid_requests_only.include(operation_id="requestRefund").parametrize()
@settings(max_examples=100, deadline=None)
def test_refunds_on_an_existing_payment_follow_the_contract(case: ApiCase) -> None:
    """Random payment ids never exist, so aim at one that does to reach 201 and 409."""
    case.path_parameters["payment_id"] = EXISTING_PAYMENT_ID
    case.call_and_validate()
