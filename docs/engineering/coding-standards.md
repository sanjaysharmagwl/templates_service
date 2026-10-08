# Coding standards

The test for any piece of code here: can a new team member read it, understand
why it is the way it is, and change it safely, without asking the author and
without an AI tool? Most rules below are checked by `make check`. The rest are
checked in review.

## Readability

- **Name things in the domain's words.** Use the terms in the
  [glossary](../domain/glossary.md): `refundable`, not `remaining_amt` or
  `available_balance_v2`.
- **Small functions that do one thing.** If a function needs a comment to
  separate its sections, split it. The complexity limit in `pyproject.toml`
  enforces an upper bound.
- **Comments say why, not what.** A comment that restates the next line is
  noise. A comment that explains a business reason or a non-obvious constraint
  is valuable.
- **No speculative code.** No unused parameters, no configuration for cases
  that do not exist, no abstraction with a single implementation unless it is
  a port. Add them when the second case arrives.
- **No dead or commented-out code.** Git remembers it.
- **Match the surrounding code.** A reader should not be able to tell which
  parts were written by whom, or by what.

## Structure

- Follow the layering in [architecture/overview.md](../architecture/overview.md).
  Business rules live in `domain`; `api` and `adapters` contain none.
- A rule is implemented in exactly one place, on the object that owns the data.
- Dependencies are passed in, not reached for. Use cases receive their
  repositories and clock through the constructor.
- Domain objects are plain dataclasses. Value objects are frozen.

## Types

- Everything is type-annotated; mypy runs in strict mode.
- Use distinct types for identifiers (`PaymentId`, `RefundId`) so they cannot
  be swapped by accident.
- No `Any` in domain or application code.

## Money

- Use `Decimal` and the `Money` type. `float` never holds an amount, not even
  temporarily.
- An amount always travels with its currency.
- Do not round. If an amount does not fit the currency's decimal places,
  reject it. A spec that needs rounding must name the rounding mode.
- On the wire, amounts are decimal strings (`"25.00"`), never JSON numbers.
- Decision record: [ADR 0002](../architecture/adr/0002-money-representation.md).

## Time

- All datetimes are timezone-aware and in UTC. Convert at the edge only.
- Code that needs the current time receives a clock. It never calls
  `datetime.now()` itself, so tests can control time.

## Errors

- A broken business rule raises a subclass of `DomainError` with a message
  that is safe to show a client.
- Each error maps to one HTTP status and one stable `ErrorCode` in
  `api/errors.py`. Clients branch on the code, never on the message.
- Do not catch an exception unless you can do something useful with it.
- Error messages and logs never contain rejected input, card or account
  numbers, credentials or personal data.

## APIs

- Every operation has an `operation_id`, a summary, and every response it can
  return documented.
- Request models forbid unknown fields.
- Any operation that changes money or state accepts an `Idempotency-Key` and
  is safe to retry.
- Changing the contract requires a spec. Removing or renaming anything is a
  breaking change.

## Dependencies

- Prefer the standard library. Each new dependency is a long-term cost and a
  supply-chain risk.
- State why a dependency is needed in the pull request that adds it.
- `uv.lock` is committed. CI installs with `--locked`.

## Suppressing checks

`# noqa`, `# type: ignore` and coverage exclusions are a last resort. Each one
needs a comment giving the reason and is reviewed like any other code.
