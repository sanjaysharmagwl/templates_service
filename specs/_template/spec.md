# NNNN: Title, as an outcome ("Refund a captured payment")

| Field | Value |
|---|---|
| Status | Draft |
| Owner | (engineer accountable for this spec) |
| Approved by | (domain owner and date, once approved) |
| Plan | [plan.md](plan.md) |

## Why

The problem, who has it, and what happens today. Two or three sentences. Link
the ticket or request.

## Scope

In scope:

- ...

Out of scope:

- ... (be explicit; this prevents the most misunderstandings)

## Terms

Terms this spec relies on, defined in
[docs/domain/glossary.md](../../docs/domain/glossary.md). Add new ones there.

## Behaviour

Describe what a caller does and what they get back. Include an example request
and response for API features.

### Rules

Single sentences that are always true. Number them and never renumber.

- **R1** ...
- **R2** ...

## Acceptance criteria

State the shared starting situation once, then one section per criterion.
Use concrete values. Cover the normal case, each boundary, and what is stored
when a request is rejected.

### AC-1: Short title

- **Given** ...
- **When** ...
- **Then** ...
- **And** ...

### AC-2: Short title

- **Given** ...
- **When** ...
- **Then** ...

## Non-functional requirements

Address each, or write "not applicable" with a reason.

- **Money:** currencies, decimal places, rounding.
- **Idempotency:** what happens when the same request arrives twice.
- **Concurrency:** what happens when two requests arrive together.
- **Audit:** what must be recorded, and for how long.
- **Privacy:** what must never appear in responses or logs.
- **Authorisation:** who may do this.
- **Performance:** expected volume and acceptable latency.

## Open questions

Anything not yet decided. A spec with unanswered questions is not ready for
approval. Keep answered questions here as a record.

| Question | Answer | Decided by |
|---|---|---|
| | | |

## Change log

| Date | Change |
|---|---|
| | Drafted. |
