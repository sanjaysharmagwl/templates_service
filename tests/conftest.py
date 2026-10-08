"""Fixtures shared by every test level."""

import pytest
from fastapi.testclient import TestClient

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.main import create_app


@pytest.fixture
def payments() -> InMemoryPaymentRepository:
    return InMemoryPaymentRepository()


@pytest.fixture
def client(payments: InMemoryPaymentRepository) -> TestClient:
    """An HTTP client for the service, backed by the `payments` repository."""
    return TestClient(create_app(payments))
