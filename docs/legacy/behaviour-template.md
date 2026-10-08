# Legacy behaviour: (capability)

| Field | Value |
|---|---|
| Legacy system | (name, repository, version or commit examined) |
| Capability | (for example: refunds) |
| Drafted by | (name; note if an AI agent produced the first draft) |
| Reviewed by | (domain owner and date) |

## Entry points

How this capability is invoked: endpoints, queue messages, scheduled jobs,
screens. Include the ones nobody remembers.

## Behaviours

One row per behaviour. Classification is the drafter's reading of the code;
Decision is the domain owner's.

| ID | Behaviour, with a concrete example | Where in the legacy code | Classification | Decision |
|---|---|---|---|---|
| L-1 | (what happens, in domain terms) | (file and function) | rule / quirk / unknown | keep / change / drop |
| L-2 | | | | |

## Data

What is read and written, and what each field means. Note fields whose meaning
differs from their name, and values with special meaning (0, -1, empty string).

## Side effects

Everything that happens beyond the response: ledger entries, emails, audit
rows, messages to other systems, files written.

## Things that are easy to lose in a rewrite

- Rounding and the order of arithmetic operations:
- Defaults applied when a value is missing:
- Duplicate and retry handling:
- Hard-coded limits, dates and special cases:
- Errors that are swallowed:
- Behaviour that depends on configuration or environment:

## Questions for the domain owner

| Question | Answer | Answered by |
|---|---|---|
| | | |
