---
name: implement-spec
description: Implement a task from an approved spec, contract first and test first. Use when asked to build, implement or code a feature that has a spec under specs/ with status Approved.
---

# Implement a spec

Work on one task from the spec's `plan.md` at a time. Each task ends with
`make check` passing and is small enough to review in one sitting.

## Before you start

- The spec's Status is `Approved`. If it is `Draft`, stop and ask for approval.
- There are no unanswered open questions that affect this task. If there are,
  stop and ask.
- Read the spec, its plan, `docs/architecture/overview.md` and
  `docs/engineering/coding-standards.md`.
- Look at how an existing feature is built before adding a new one. Spec 0001
  is the reference: follow its files from `api/refunds.py` inwards.

## Steps

1. **Contract.** If the task changes the API, edit `api/schemas.py` and add the
   route with its documented responses. Run `make openapi` and read the diff of
   `contracts/openapi.json`. Removing or renaming anything a client uses is a
   breaking change and needs to be called out in the spec.
2. **Failing tests.** For each acceptance criterion in the task:
   - write an acceptance test in `tests/acceptance/test_NNNN_<name>.py` that
     goes through HTTP, marked `@pytest.mark.covers("NNNN:AC-n")`;
   - write unit tests for the rule itself in `tests/unit/`;
   - for a rule that must hold for all inputs (totals, limits, idempotency),
     add a property-based test.
   Run them and confirm they fail for the right reason.
3. **Domain.** Put the rule in the domain object that owns the data. Raise a
   `DomainError` subclass when a rule is broken. No framework imports.
4. **Application.** Add or extend a use case that loads, calls the domain,
   and saves. If it needs something from outside, add a port in
   `application/ports.py`.
5. **Adapters and API.** Implement new ports. Map new errors to a status and
   an `ErrorCode` in `api/errors.py`. Wire new use cases in `main.py`.
6. **Check.** Run `make check`. Fix the code, not the checks.
7. **Finish.** Tick the task in `plan.md`. When the last task is done, set the
   spec's Status to `Implemented`; `make trace` then requires every criterion
   to have a test.

## If something does not fit

- A criterion is ambiguous, contradicts another, or cannot be met: stop, write
  the question under "Open questions" in the spec, and ask.
- You need behaviour the spec does not mention: that is a spec change. Propose
  it; do not build it silently.
- An existing test fails because of your change: the test is probably right.
  Never edit it to pass without a human agreeing the old behaviour was wrong.

## Report when done

State which criteria the change covers, the contract diff (or "no contract
change"), any new dependency and why, and anything you were unsure about.
