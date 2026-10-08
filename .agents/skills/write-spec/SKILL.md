---
name: write-spec
description: Turn a requirement, ticket or conversation into a spec under specs/. Use when asked to specify, scope or design a feature or behaviour change, and before writing code for anything that has no approved spec.
---

# Write a spec

A spec states what the service must do, precisely enough that two engineers
would build the same behaviour and a tester could check it. It says nothing
about how the code is organised; that goes in `plan.md`.

## Steps

1. **Read first.** `docs/domain/glossary.md`, the specs that touch the same
   area, and the relevant ADRs in `docs/architecture/adr/`. When replacing
   legacy behaviour, read the matching file in `docs/legacy/`.
2. **Create the folder.** Copy `specs/_template/` to `specs/NNNN-short-name/`,
   where `NNNN` is the next unused number. Set Status to `Draft`.
3. **Write Why and Scope.** One paragraph on the problem and who has it. List
   what is out of scope explicitly; it prevents the most arguments later.
4. **Write the rules.** Number them R1, R2, and so on. Each rule is one
   sentence that is always true, for example "The refunds on a payment never
   add up to more than its captured amount."
5. **Write the acceptance criteria.** Number them AC-1, AC-2, and so on, each
   under its own `### AC-n: title` heading, in Given / When / Then form with
   concrete values. Include, for every rule:
   - the normal case,
   - the boundary (exactly at the limit, and just past it),
   - what happens to stored data when the request is rejected.
6. **Cover what financial services always need.** For each item, either write
   a criterion or state in the spec that it does not apply:
   - currency and decimal places; rounding (the default here is to reject);
   - retries and duplicate requests (idempotency);
   - two requests arriving at the same time;
   - what must be recorded for audit, and what must never be logged;
   - who is allowed to do this.
7. **Add new terms** to `docs/domain/glossary.md` and use them consistently.
8. **List open questions.** Anything you had to assume goes under "Open
   questions" as a question for a named person. Do not resolve business
   questions yourself.
9. **Write `plan.md`** only after the criteria are stable: approach, affected
   layers, contract changes, test plan, and tasks of one pull request each.
10. **Stop for approval.** Open a pull request containing only the spec and
    plan. A human sets Status to `Approved`. No code before that.

## Check before handing over

- Every criterion can be checked by a test with a clear pass or fail.
- No criterion describes implementation ("store in table X", "use class Y").
- Every number has a unit and every amount has a currency.
- No open question is hidden inside a criterion as an assumption.
- `make trace` passes.
