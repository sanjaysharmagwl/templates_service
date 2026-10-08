# How we build: from requirement to merged code

The same six steps apply whether a person or an AI agent does the work. Each
step produces a file in this repository, and each file is readable without any
particular tool. If AI assistance is unavailable, nothing here changes.

| Step | Output | Done when |
|---|---|---|
| 1. Spec | `specs/NNNN-name/spec.md` | A domain owner approved it |
| 2. Plan | `specs/NNNN-name/plan.md` | An engineer reviewed it |
| 3. Contract | `api/schemas.py`, `contracts/openapi.json` | The diff matches the spec |
| 4. Tests | `tests/` | One failing test per acceptance criterion |
| 5. Code | `src/` | `make check` passes |
| 6. Review | Pull request | A human approved and merged it |

## 1. Spec

Write what the service must do and how we will know it does: rules, and
acceptance criteria in Given / When / Then form with concrete values. Start
from [`specs/_template/`](../../specs/_template/); the conventions are in
[`specs/README.md`](../../specs/README.md).

A spec is reviewed in its own pull request, before any code exists. This is the
cheapest point to find a misunderstanding. The person who owns the business
rule approves it by setting Status to `Approved`.

An agent can draft a spec from a ticket or a conversation. Deciding what the
business wants is not delegated: open questions go to a named person.

## 2. Plan

Write how the spec will be built: which layers change, what happens to the
contract, which test covers which criterion, and a list of tasks. Size each
task to be one pull request that a reviewer can hold in their head.

## 3. Contract

Change the request and response models first and regenerate the contract with
`make openapi`. Reviewing the diff of `contracts/openapi.json` shows exactly
what clients will see, before the behaviour exists.

CI compares the contract with the one on the target branch and fails on a
breaking change. A deliberate breaking change needs the
`breaking-change-approved` label on the pull request, applied by a code owner.

## 4. Tests

Write the tests for the task and watch them fail. Mark each test with the
criterion it verifies:

```python
@pytest.mark.covers("0001:AC-3")
def test_refund_larger_than_the_refundable_amount_is_rejected(...): ...
```

`make trace` checks that every criterion of an implemented spec has a test and
that every marker points at a criterion that exists. See
[testing.md](testing.md) for which kind of test goes where.

## 5. Code

Write the simplest code that passes, inside the layering rules in
[architecture/overview.md](../architecture/overview.md) and the
[coding standards](coding-standards.md). Run `make check`.

## 6. Review

Open a pull request using the template. The reviewer reads the spec, then the
tests, then the contract diff, then the code. The author is accountable for
every line, whoever or whatever typed it.

## Definition of done

- The spec is `Approved`, and `Implemented` once its last task is merged.
- Every acceptance criterion has a test marked `covers`.
- `make check` passes locally and in CI.
- `contracts/openapi.json` is regenerated and its diff was reviewed.
- New terms are in the glossary; new decisions have an ADR.
- A human reviewed and approved the pull request.

## Changing behaviour that already exists

Edit the spec first, in a pull request that shows the old and new criteria side
by side. Then change the tests, then the code. If a spec is replaced entirely,
set its Status to `Superseded` and link the new one.

## Bugs

A bug is a difference between the spec and the code, or a case the spec missed.

- The code disagrees with the spec: write a failing test for the criterion, fix
  the code.
- The spec missed the case: add a criterion to the spec, get it approved, then
  test and fix.

## Small changes

Refactoring, dependency updates and fixes with no change in behaviour need no
spec. The existing tests must pass unchanged, which is the evidence that
behaviour did not change.
