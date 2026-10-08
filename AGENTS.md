# AGENTS.md

Instructions for AI coding agents working in this repository. Human engineers
follow the same rules; the full versions are in [docs/engineering/](docs/engineering/).

## Commands

| Command | Use |
|---|---|
| `make setup` | Install dependencies (uv) and git hooks |
| `make check` | Lint, types, layering, tests, spec traceability. **Must pass before you report a task as done.** |
| `make format` | Format and apply safe lint fixes |
| `make openapi` | Regenerate `contracts/openapi.json` after an intended API change |
| `make run` | Local server with sample data |

Run a single test with `uv run pytest tests/unit/test_payment.py -k refund`.

## How work is done here

Every change in behaviour follows the same four steps. Each has a runbook.

1. **Spec.** Behaviour is defined in `specs/NNNN-name/spec.md` before any code.
   If there is no spec with status `Approved` for what you were asked to build,
   write or update the spec and stop for human approval.
   Runbook: `.agents/skills/write-spec/SKILL.md`
2. **Contract.** Change the request and response schemas first, run
   `make openapi`, and show the diff of `contracts/openapi.json`.
3. **Tests.** Write a failing test for each acceptance criterion, marked
   `@pytest.mark.covers("NNNN:AC-n")`, before the code that satisfies it.
4. **Code.** Write the simplest code that makes the tests pass.
   Runbook for steps 2 to 4: `.agents/skills/implement-spec/SKILL.md`

Other runbooks: `.agents/skills/review-change/SKILL.md` (reviewing a change),
`.agents/skills/document-legacy-behaviour/SKILL.md` (rewriting an existing system).

## Where things are

| Path | Contents |
|---|---|
| `specs/` | Requirements and acceptance criteria. The source of truth for behaviour. |
| `contracts/openapi.json` | The API contract. Generated; never edit by hand. |
| `docs/domain/glossary.md` | Domain terms. Use these exact words in code and specs. |
| `docs/architecture/` | Layering rules and decision records (ADRs) |
| `docs/engineering/` | Coding standards, testing strategy, workflow |
| `src/service_template/` | `domain` → `application` → `adapters`, `api` → `main` |
| `tests/` | `unit`, `acceptance`, `contract`, `characterization` |

## Rules

- **Layering.** `domain` and `application` never import FastAPI, Pydantic or
  any I/O library. Dependencies point inwards. `make check` enforces this.
- **Money.** `Decimal` and the `Money` type only, never `float`. Reject
  amounts that do not fit the currency; do not round.
- **Time.** Timezone-aware UTC, obtained through the injected clock.
- **Errors.** Business-rule violations are `DomainError` subclasses, mapped to
  HTTP in `api/errors.py`. Error responses never contain rejected input.
- **Style.** Write code a new team member can read without help: plain names
  from the glossary, small functions, comments only for *why*. Match the code
  already in the repository.
- **Size.** One task from the spec's plan per pull request.

## Never

- Change, weaken, skip or delete a test to make it pass. If a test looks
  wrong, say so and stop.
- Change an acceptance criterion in an approved spec without human approval.
- Edit `contracts/openapi.json` by hand, or change the contract without a spec.
- Put secrets, credentials or real customer data in code, tests, fixtures or logs.
- Add a dependency without stating why in the pull request.
- Add `# noqa`, `# type: ignore` or coverage exclusions to get past a check.

## When unsure

Stop and ask. Record the question under "Open questions" in the spec rather
than guessing: a wrong assumption about money is expensive to undo.
