"""The committed contract must match what the code actually serves.

contracts/openapi.json is the reviewed, versioned description of the API. If
this test fails, the API changed: run `make openapi`, read the diff, and make
sure the change is covered by a spec before committing it.
"""

import json
from pathlib import Path

from service_template.main import create_app

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "openapi.json"


def test_committed_contract_matches_the_running_api() -> None:
    committed = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert create_app().openapi() == committed, (
        "contracts/openapi.json is out of date. Run `make openapi` and review the diff."
    )
