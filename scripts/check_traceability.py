"""Check that specs and tests agree on the acceptance criteria.

Two rules:

1. Every `@pytest.mark.covers("<spec id>:AC-<n>")` in tests/ points at an
   acceptance criterion that exists in a spec.
2. Every acceptance criterion of a spec whose status is Implemented is covered
   by at least one test.

Run it with `make trace`. It reads files as text and needs nothing installed.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = ROOT / "specs"
TESTS_DIR = ROOT / "tests"

SPEC_DIR_NAME = re.compile(r"^(\d{4})-")
STATUS_ROW = re.compile(r"^\|\s*Status\s*\|\s*(\w+)\s*\|", re.MULTILINE)
CRITERION_HEADING = re.compile(r"^#{2,4}\s+(AC-\d+)\b", re.MULTILINE)
COVERS_MARKER = re.compile(r"covers\(\s*[\"'](\d{4}):(AC-\d+)[\"']\s*\)")


@dataclass(frozen=True)
class Spec:
    spec_id: str
    name: str
    status: str
    criteria: frozenset[str]


def load_specs() -> list[Spec]:
    specs = []
    for spec_file in sorted(SPECS_DIR.glob("*/spec.md")):
        name = spec_file.parent.name
        match = SPEC_DIR_NAME.match(name)
        if match is None:
            continue  # the template folder
        text = spec_file.read_text(encoding="utf-8")
        status = STATUS_ROW.search(text)
        specs.append(
            Spec(
                spec_id=match.group(1),
                name=name,
                status=status.group(1) if status else "Unknown",
                criteria=frozenset(CRITERION_HEADING.findall(text)),
            )
        )
    return specs


def load_covered_criteria() -> dict[tuple[str, str], list[Path]]:
    covered: dict[tuple[str, str], list[Path]] = {}
    for test_file in sorted(TESTS_DIR.rglob("test_*.py")):
        text = test_file.read_text(encoding="utf-8")
        for spec_id, criterion in COVERS_MARKER.findall(text):
            covered.setdefault((spec_id, criterion), []).append(test_file)
    return covered


def find_problems(specs: list[Spec], covered: dict[tuple[str, str], list[Path]]) -> list[str]:
    problems = []
    known = {(spec.spec_id, criterion) for spec in specs for criterion in spec.criteria}

    for (spec_id, criterion), test_files in sorted(covered.items()):
        if (spec_id, criterion) not in known:
            where = test_files[0].relative_to(ROOT)
            problems.append(f"{where}: covers {spec_id}:{criterion}, which no spec defines")

    for spec in specs:
        if spec.status == "Unknown":
            problems.append(f"specs/{spec.name}/spec.md: no Status row in the header table")
        if spec.status != "Implemented":
            continue
        for criterion in sorted(spec.criteria, key=_criterion_number):
            if (spec.spec_id, criterion) not in covered:
                problems.append(
                    f"specs/{spec.name}/spec.md: {criterion} has no test "
                    f'(add @pytest.mark.covers("{spec.spec_id}:{criterion}"))'
                )
    return problems


def _criterion_number(criterion: str) -> int:
    return int(criterion.removeprefix("AC-"))


def main() -> int:
    specs = load_specs()
    covered = load_covered_criteria()

    for spec in specs:
        tested = sum((spec.spec_id, criterion) in covered for criterion in spec.criteria)
        print(f"{spec.name} [{spec.status}]: {tested}/{len(spec.criteria)} criteria have tests")

    problems = find_problems(specs, covered)
    for problem in problems:
        print(f"ERROR {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
