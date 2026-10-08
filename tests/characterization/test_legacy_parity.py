"""Characterization tests: the new service must behave as the old one did.

Each JSON file in `cases/` is one request and response recorded from the
legacy system. This test replays every case against the new service and
compares the result. See docs/legacy/README.md for how to record cases.

The cases shipped with the template are illustrative samples, not recordings.
Replace them with real ones, or delete this folder if nothing is being rewritten.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from service_template.adapters.in_memory import InMemoryPaymentRepository
from tests.factories import captured_payment, inr

CASES = sorted((Path(__file__).parent / "cases").glob("*.json"))


@pytest.mark.parametrize("case_file", CASES, ids=lambda path: path.stem)
def test_new_service_matches_recorded_legacy_behaviour(
    case_file: Path, client: TestClient, payments: InMemoryPaymentRepository
) -> None:
    case = json.loads(case_file.read_text(encoding="utf-8"))
    given, when, then = case["given"], case["when"], case["then"]
    payments.save(captured_payment(given["payment_id"], inr(given["captured_inr"])))

    response = client.post(
        f"/v1/payments/{given['payment_id']}/refunds",
        headers={"Idempotency-Key": when["idempotency_key"]},
        json=when["body"],
    )

    assert response.status_code == then["status"]
    assert _selected(response.json(), then["body"]) == then["body"]


def _selected(actual: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    """The fields of `actual` that the recorded case makes a statement about.

    Generated values such as identifiers and timestamps differ between systems,
    so a case lists only the fields that must match.
    """
    return {field: actual.get(field) for field in expected}
