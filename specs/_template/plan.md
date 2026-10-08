# Plan for NNNN: Title

The spec says *what*. This plan says *how*, and breaks the work into tasks
small enough to review one at a time. Write it after the acceptance criteria
are stable.

## Approach

The design in a few sentences: which object owns each rule, and any decision
worth explaining. Link an ADR for decisions that outlive this feature.

| Layer | Change |
|---|---|
| domain | |
| application | |
| adapters | |
| api | |

## Contract

Operations added or changed, their status codes, and whether anything is a
breaking change for existing clients. Write "no contract change" if so.

## Test plan

| Criterion | Unit | Acceptance |
|---|---|---|
| AC-1 | | |
| AC-2 | | |

List any invariant that needs a property-based test.

## Tasks

Each task is one pull request that leaves `make check` passing.

- [ ] 1. Contract: schemas, route stub, `contracts/openapi.json`
- [ ] 2. ...
- [ ] n. Set the spec status to Implemented

## Risks

What could go wrong, and what is deliberately left for later.
