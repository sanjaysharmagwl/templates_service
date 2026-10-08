"""Rename the service, for starting a new project from this template.

    uv run python scripts/rename_service.py payments-ledger

Replaces the project name (`service-template`), the Python package name
(`service_template`) and the display name (`Service Template`) in every text
file, and renames the package directory. The current name is read from
pyproject.toml, so the script can be run again later.

Afterwards run `uv sync` and `make check`.
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SKIPPED_DIRS = {
    ".git",
    ".venv",
    ".hypothesis",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}


def package_name(project_name: str) -> str:
    return project_name.replace("-", "_")


def display_name(project_name: str) -> str:
    return project_name.replace("-", " ").title()


def current_project_name() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    name: str = pyproject["project"]["name"]
    return name


def text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not SKIPPED_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def replace_in_file(path: Path, replacements: dict[str, str]) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False  # binary file
    updated = original
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) != 2 or not VALID_NAME.match(sys.argv[1]):
        print("usage: rename_service.py <new-name>   (lowercase, e.g. payments-ledger)")
        return 2

    old_name, new_name = current_project_name(), sys.argv[1]
    if old_name == new_name:
        print(f"The service is already called {new_name}.")
        return 0

    replacements = {
        old_name: new_name,
        package_name(old_name): package_name(new_name),
        display_name(old_name): display_name(new_name),
    }
    changed = [path for path in text_files() if replace_in_file(path, replacements)]

    old_package = ROOT / "src" / package_name(old_name)
    if old_package.is_dir():
        old_package.rename(ROOT / "src" / package_name(new_name))

    print(f"Renamed {old_name} to {new_name} in {len(changed)} files.")
    print("Next: run `uv sync`, then `make check`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
