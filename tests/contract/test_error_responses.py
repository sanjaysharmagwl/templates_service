"""Every error leaves the service in the same shape, whatever caused it."""

from fastapi.testclient import TestClient

from service_template.domain.payment import Payment, PaymentId
from service_template.main import create_app


class BrokenPaymentRepository:
    """Simulates the database being unavailable."""

    def get(self, payment_id: PaymentId) -> Payment | None:
        raise ConnectionError(f"db-primary.internal:5432 refused connection for {payment_id}")

    def save(self, payment: Payment) -> None:
        raise ConnectionError("db-primary.internal:5432 refused connection")


def test_unexpected_failures_do_not_leak_internal_details() -> None:
    client = TestClient(create_app(BrokenPaymentRepository()), raise_server_exceptions=False)

    response = client.post(
        "/v1/payments/pay_1/refunds",
        headers={"Idempotency-Key": "key-1"},
        json={"amount": {"value": "10.00", "currency": "INR"}},
    )

    assert response.status_code == 500
    assert response.json() == {
        "code": "internal_error",
        "message": "internal server error",
        "details": [],
    }


def test_unknown_routes_use_the_standard_error_shape(client: TestClient) -> None:
    response = client.get("/v1/no-such-resource")

    assert response.status_code == 404
    assert response.json() == {"code": "not_found", "message": "Not Found", "details": []}


def test_wrong_method_names_the_allowed_ones(client: TestClient) -> None:
    response = client.delete("/healthz")

    assert response.status_code == 405
    assert response.json()["code"] == "method_not_allowed"
    assert response.headers["allow"] == "GET"


def test_unreadable_body_is_a_bad_request(client: TestClient) -> None:
    response = client.post(
        "/v1/payments/pay_1/refunds",
        headers={"Idempotency-Key": "key-1", "Content-Type": "application/json"},
        content=b"\xff\xfe not json",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "bad_request"
