# Rewriting an existing system

Use this process when a service is being rewritten from existing source code.
Delete this folder and `tests/characterization/` if nothing is being rewritten.

## Why not translate the code

Old code contains three things mixed together: business rules, accidents that
callers now depend on, and workarounds for problems that no longer exist.
Translating it, by hand or with an AI agent, carries all three into the new
service without anyone deciding which to keep. The result is new code with old
problems and no record of why it behaves as it does.

Instead, recover the *behaviour*, let people who know the business decide what
to keep, write a spec, and build from the spec.

## The process

| Stage | Output | Who decides |
|---|---|---|
| 1. Describe | `docs/legacy/<capability>.md` | Engineer or agent drafts |
| 2. Classify | Each behaviour marked keep, change or drop | Domain owner |
| 3. Characterize | `tests/characterization/cases/*.json` | Engineer |
| 4. Specify | `specs/NNNN-name/spec.md` | Domain owner approves |
| 5. Build | Code and tests, per the normal [workflow](../engineering/workflow.md) | Reviewer |
| 6. Compare | Old and new run side by side | Team |
| 7. Cut over | Traffic moved, old code retired | Team |

Work through one capability at a time, not the whole system.

### 1. Describe

Read the old code for one capability and write down what it does, as a
numbered list of behaviours (L-1, L-2 and so on), each with a concrete example
and a pointer to where it is implemented. Start from
[behaviour-template.md](behaviour-template.md).

This is a good task for an AI agent, which can read a large codebase quickly.
Its output is a draft. It will miss behaviour that lives in database triggers,
scheduled jobs, configuration and other systems, and it cannot know intent.

### 2. Classify

A domain owner reviews every item and marks it:

- **keep**: the new service must do the same;
- **change**: the new service must do something different, stated explicitly;
- **drop**: no longer needed.

Items nobody can explain are the important ones. Find out before deciding.

### 3. Characterize

For each item marked keep, record real inputs and outputs of the old system as
JSON cases in `tests/characterization/cases/`.
`tests/characterization/test_legacy_parity.py` replays every case against the
new service. Remove or replace customer data before a case is committed.

The two cases shipped with the template are illustrative samples. Replace them.

### 4. Specify

Write the spec for the new service. Kept items become rules and acceptance
criteria. Changed items become criteria that state the new behaviour and note
the difference from the old one, so the change is visible to reviewers and to
whoever handles questions after cut-over.

### 5. Build

Follow the normal workflow. The new code is designed for the new spec; it does
not need to resemble the old code, its tables or its names.

### 6. Compare

Before switching, run both systems on the same inputs and compare outputs:
replay recorded traffic against the new service, or send live requests to both
and discard the new service's response. Investigate every difference. Each one
is either a bug in the new service, a deliberate change that should already be
in the spec, or an undocumented legacy behaviour to take back to stage 2.

### 7. Cut over

Move traffic gradually and keep the ability to switch back. When the old
service is retired, keep the characterization cases that are still meaningful
as regression tests and delete the rest.
