---
name: document-legacy-behaviour
description: Extract what an existing system does into a reviewable behaviour document and characterization tests, as the first step of rewriting it. Use when asked to rewrite, migrate, port or replace a service or module from existing source code.
---

# Document legacy behaviour

Do not translate old code into new code. The old code mixes rules, accidents
and workarounds, and a translation carries all three across unseen. Instead,
write down what the old system does, let a person who knows the business
decide what to keep, and build the new service from a spec.

The full process is in `docs/legacy/README.md`. This runbook covers the first
two stages.

## Stage 1: Describe the behaviour

For one capability at a time (for example "refunds", not "the payments module"):

1. Copy `docs/legacy/behaviour-template.md` to `docs/legacy/<capability>.md`.
2. Read the legacy code along the whole path: entry points, validation,
   calculations, writes, calls to other systems, scheduled jobs that touch the
   same data.
3. Record each behaviour as a numbered item, L-1, L-2, and so on, with:
   - what happens, in domain terms, with a concrete example;
   - where it is in the legacy code (file and function), so it can be checked;
   - a classification: **rule** (intended), **quirk** (looks accidental) or
     **unknown** (cannot tell from the code).
4. Look specifically for what rewrites usually lose:
   - rounding and the order of arithmetic operations;
   - defaults applied when a field is missing or null;
   - what is treated as a duplicate, and what happens on retry;
   - hard-coded limits, dates, customer or currency special cases;
   - side effects: emails, ledger entries, audit rows, messages to other systems;
   - error cases that are swallowed or logged and ignored.
5. List what you could not determine from the code under "Questions for the
   domain owner". Do not guess.

The document is a draft until a domain owner has reviewed every item and
marked it **keep**, **change** or **drop**. That decision is theirs.

## Stage 2: Capture characterization cases

For each item marked **keep**:

1. Record real request and response pairs from the legacy system, or derive
   them from its tests. Remove or replace any real customer data before the
   case enters the repository.
2. Save each as a JSON file in `tests/characterization/cases/` in the format
   used there, referencing the item (`L-3`) in its description.
3. Add cases for the boundaries, not only the normal path.

These cases fail until the new service is built. That is expected.

## Then

Write the spec for the new service with the `write-spec` runbook. Each kept
item becomes a rule or an acceptance criterion; each changed item becomes a
criterion that states the new behaviour and why it differs.

## Do not

- Copy legacy code, table layouts or names into the new service by default.
- Decide yourself that a quirk is a bug. Record it and ask.
- Include production data, credentials or connection strings in the document.
