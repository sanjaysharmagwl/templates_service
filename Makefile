# One entry point for humans, AI agents and CI. `make check` is the gate:
# if it passes locally, CI passes.

.DEFAULT_GOAL := help
.PHONY: help setup check format lint typecheck arch test trace openapi run agent-links clean

help:  ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup:  ## Install dependencies and git hooks
	uv sync
	@if [ -d .git ]; then uv run pre-commit install; fi

check: lint typecheck arch test trace  ## Run every check CI runs

format:  ## Format the code and apply safe lint fixes
	uv run ruff format .
	uv run ruff check --fix .

lint:  ## Check formatting and lint rules
	uv run ruff format --check .
	uv run ruff check .

typecheck:  ## Check types (mypy, strict)
	uv run mypy

arch:  ## Check the layering rules (import-linter)
	uv run lint-imports

test:  ## Run all tests with coverage
	uv run pytest

trace:  ## Check every acceptance criterion has a test
	uv run python scripts/check_traceability.py

openapi:  ## Regenerate contracts/openapi.json from the code
	uv run python scripts/export_openapi.py

run:  ## Start a local server with sample data on http://127.0.0.1:8000
	uv run python scripts/dev_server.py

agent-links:  ## Link .agents/skills into tool-specific folders
	uv run python scripts/link_agent_skills.py

clean:  ## Remove caches and build output
	rm -rf .mypy_cache .pytest_cache .ruff_cache .import_linter_cache .hypothesis .coverage dist
	find . -name __pycache__ -type d -not -path './.venv/*' -prune -exec rm -rf {} +
