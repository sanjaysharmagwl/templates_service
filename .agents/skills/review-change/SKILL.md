---
name: review-change
description: Review a pull request or a set of local changes against the spec and the team's standards. Use when asked to review, check or give feedback on a change before it is merged.
---

# Review a change

The question a review answers is: does this change do what the spec says, and
nothing else, in code the team can maintain? Who or what wrote the code makes
no difference to the standard.

## Steps

1. **Find the spec.** The pull request must link one. Read the acceptance
   criteria it claims to cover before reading the diff. A behaviour change
   with no spec is the first finding.
2. **Run the gate.** `make check` must pass on the branch.
3. **Read the tests first.** For each claimed criterion:
   - is there a test marked `covers` for it, and does the test assert what the
     criterion says, including that rejected requests change nothing?
   - would the test fail if the rule were removed? A test that cannot fail is
     a finding.
   - were any existing tests edited or deleted? Each one needs a stated reason.
4. **Read the contract diff.** Any change to `contracts/openapi.json` must be
   intended by the spec. Look for removed fields, new required fields,
   narrowed types and changed status codes.
5. **Read the code**, from the domain outwards:
   - is each rule in the domain, in one place?
   - money: `Decimal` and `Money` only, no rounding, currency checked;
   - time: timezone-aware, from the injected clock;
   - errors: nothing sensitive in messages or logs;
   - concurrency: what happens if this runs twice at once?
   - is there anything the spec did not ask for?
6. **Read it as a newcomer.** Could a new team member follow this without
   asking the author? Flag unclear names, cleverness, dead code, comments that
   restate the code, and abstractions with one use.
7. **Check the leftovers.** New dependencies justified; no secrets or real
   customer data; no new `noqa`, `type: ignore` or coverage exclusions.

## Report

List findings most serious first. For each: the file and line, what is wrong,
and a concrete suggestion. Separate what must change before merge from what is
optional. If nothing is wrong, say so plainly and say what you checked.
