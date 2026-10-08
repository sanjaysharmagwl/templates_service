"""Write the API's OpenAPI document to contracts/openapi.json.

Run it with `make openapi` after an intended API change, then review the diff
like any other code change: that file is the contract clients rely on.
"""

import json
from pathlib import Path

from service_template.main import create_app

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "openapi.json"


def main() -> None:
    document = create_app().openapi()
    CONTRACT.parent.mkdir(exist_ok=True)
    CONTRACT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CONTRACT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
