# Service Template

A starting point for backend services built from written specs, by people and
AI agents working the same way. Python, FastAPI, uv, GitHub.

It contains a small working example, refunds against a captured payment, taken
through every step: spec, contract, tests, code. Read the example, then replace
it with your first feature.

## The idea

Everything needed to build this service correctly is a plain file in this
repository: what it must do (`specs/`), the words we use (`docs/domain/`), how
it is structured (`docs/architecture/`), the standards (`docs/engineering/`),
and one command that checks the result (`make check`).

An AI agent reads those files. So does a new engineer. Nothing depends on a
particular AI tool or model, and if none is available the team works the same
way, a little slower.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and `make`. On Windows, use WSL, or
run the commands listed in the `Makefile` directly.

```bash
make setup     # install dependencies and git hooks
make check     # lint, types, layering, tests, spec traceability
make run       # local server with sample data: http://127.0.0.1:8000/docs
```

Try the example while the server runs:

```bash
curl -X POST http://127.0.0.1:8000/v1/payments/pay_demo/refunds \
  -H 'Idempotency-Key: demo-1' -H 'Content-Type: application/json' \
  -d '{"amount": {"value": "30.00", "currency": "INR"}, "reason": "Customer returned the item"}'
```

## How a feature is built

| Step | You produce | Checked by |
|---|---|---|
| 1. Spec | `specs/NNNN-name/spec.md`: rules and acceptance criteria | Domain owner approves the pull request |
| 2. Plan | `specs/NNNN-name/plan.md`: approach and tasks | Engineer review |
| 3. Contract | Schemas, then `make openapi` | Diff of `contracts/openapi.json`; CI blocks breaking changes |
| 4. Tests | One failing test per criterion, marked `covers("NNNN:AC-n")` | `make trace` |
| 5. Code | The simplest code that passes | `make check` |
| 6. Review | Pull request | A human approves |

Details: [docs/engineering/workflow.md](docs/engineering/workflow.md).

To see it end to end, read the example in this order:

1. [specs/0001-refund-captured-payment/spec.md](specs/0001-refund-captured-payment/spec.md)
2. [tests/acceptance/test_0001_refund_captured_payment.py](tests/acceptance/test_0001_refund_captured_payment.py)
3. [src/service_template/domain/payment.py](src/service_template/domain/payment.py)

## What is in the repository

```
AGENTS.md                 instructions for AI agents (short; points to the rest)
Makefile                  the commands everyone uses
specs/                    requirements: one folder per feature
contracts/openapi.json    the API contract, generated and reviewed
docs/
  domain/glossary.md      the team's vocabulary
  architecture/           layering rules and decision records
  engineering/            workflow, coding standards, testing, working with AI
  legacy/                 how to rewrite an existing system
src/service_template/
  domain/                 business rules, plain Python
  application/            use cases and ports
  adapters/               implementations of ports
  api/                    HTTP routes, schemas, error mapping
  main.py                 wires it together
tests/
  unit/                   rules and objects, including property-based tests
  acceptance/             one test per acceptance criterion, over HTTP
  contract/               the API matches its contract
  characterization/       the new service matches recorded legacy behaviour
.agents/skills/           runbooks: write a spec, implement one, review, document legacy code
.github/                  CI, pull request template, code owners
scripts/                  small helpers behind the make targets
```

## What `make check` enforces

| Check | Tool | Catches |
|---|---|---|
| Format and lint | ruff | Style, likely bugs, complexity, naive datetimes, stray prints |
| Types | mypy, strict | Type errors, missing annotations |
| Layering | import-linter | Framework or I/O imports in business code; dependencies pointing outwards |
| Tests | pytest, Hypothesis, Schemathesis | Broken rules, broken invariants, responses that violate the contract |
| Contract snapshot | pytest | An API change not reflected in `contracts/openapi.json` |
| Coverage | pytest-cov | Less than 90% branch coverage |
| Traceability | `scripts/check_traceability.py` | An acceptance criterion with no test; a test pointing at a missing criterion |

CI runs the same command, and additionally fails a pull request whose contract
change would break existing clients.

## Starting a new service from this template

1. Create a repository from this one, then rename the service:

   ```bash
   uv run python scripts/rename_service.py payments-ledger
   uv sync && make check
   ```

2. In `.github/CODEOWNERS`, replace the placeholder teams.
3. In GitHub, protect `main`: require a pull request, an approving review from
   code owners, and the checks `make check` and `API contract is backwards
   compatible`. Create the label `breaking-change-approved`.
4. Review the open decisions listed at the end of
   [docs/architecture/overview.md](docs/architecture/overview.md): database,
   sync or async, authentication, audit logging.
5. Write your first spec: copy `specs/_template/` to `specs/0002-your-feature/`.

### Removing the example

Keep the example until your first feature is merged; it is the reference for
how things fit together. Then delete:

- `specs/0001-refund-captured-payment/`
- `src/service_template/domain/payment.py`, `application/request_refund.py`,
  `api/refunds.py`, and their wiring in `main.py`, `api/errors.py`,
  `api/dependencies.py` and `api/schemas.py`
- the matching tests under `tests/`, and the sample cases in
  `tests/characterization/cases/`
- `scripts/dev_server.py`'s sample payment

`domain/money.py` is worth keeping. Run `make openapi` and `make check` afterwards.

## Working with AI agents

Point any coding agent at this repository. It should read `AGENTS.md`, which
tells it the commands, the workflow, the rules, and where the runbooks are.

- `AGENTS.md` is read natively by most coding agents.
- `CLAUDE.md` is a one-line import of `AGENTS.md`, for Claude Code.
- `.agents/skills/` holds the runbooks in the open Agent Skills format. Run
  `make agent-links` once if your tool only looks for skills in its own folder.

Typical requests:

- "Draft a spec for letting operations staff cancel a pending refund."
- "Implement task 2 of spec 0002."
- "Review my changes against spec 0002."
- "Document how refunds work in the legacy billing service at ../billing."

The rules for using agents on this codebase, including what must never go into
a prompt, are in
[docs/engineering/ai-assisted-development.md](docs/engineering/ai-assisted-development.md).

## Working without AI

Follow [docs/engineering/workflow.md](docs/engineering/workflow.md). The
runbooks in `.agents/skills/` are written as checklists a person can follow.
