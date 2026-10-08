# 0003: Specs live in the repository as plain Markdown

| Field | Value |
|---|---|
| Status | Accepted |
| Date | (date adopted) |
| Deciders | (team) |

## Context

We want to build from written requirements, with work done by people and by AI
agents interchangeably. We do not want the process to depend on one AI tool,
model or spec-driven-development framework, and we want to be able to continue
unchanged if AI assistance is unavailable.

## Decision

- Each feature has a spec at `specs/NNNN-name/spec.md` and a plan at
  `plan.md`, written in plain Markdown from a template.
- Specs are reviewed and approved through pull requests, like code.
- Acceptance criteria have identifiers (`AC-1`). Tests name the criterion they
  verify with `@pytest.mark.covers("NNNN:AC-1")`. A short script in this
  repository, `scripts/check_traceability.py`, checks the link in both
  directions.
- Instructions for AI agents are in `AGENTS.md` and `.agents/skills/`, in open
  formats. Tool-specific files only point to these.

## Alternatives considered

- **A spec-driven-development tool.** These add their own commands, file
  layouts and generated artefacts. Rejected because the process would then
  depend on the tool continuing to exist and to suit us.
- **Specs in a wiki or ticket system.** Rejected because they are not
  versioned with the code, cannot be reviewed in the same pull request, and
  are not visible to an agent working in the repository.
- **Gherkin feature files executed by a BDD framework.** A reasonable choice.
  Not chosen because the extra layer of step definitions is more to maintain
  than a marker on an ordinary pytest test.

## Consequences

- Anyone can read the full history of a requirement with `git log`.
- The only tooling involved is a Markdown file and a small script we own.
- Keeping specs current is a discipline: a behaviour change without a spec
  change must be caught in review.
