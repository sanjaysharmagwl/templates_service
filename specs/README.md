# Specs

Every change in what the service does starts here. A spec says what must be
true and how we will check it. Code follows the spec; when they disagree, one
of them has a bug.

## Layout

```
specs/
├── _template/            copy this to start a new spec
│   ├── spec.md
│   └── plan.md
└── 0001-refund-captured-payment/
    ├── spec.md           what and why: rules and acceptance criteria
    └── plan.md           how: approach, test plan, tasks
```

Number specs in order of creation. The number never changes and is never reused.

## Status

Each spec has a Status row in its header table.

| Status | Meaning | Who sets it |
|---|---|---|
| `Draft` | Being written. No code yet. | Author |
| `Approved` | Agreed. Implementation may start. | Domain owner |
| `Implemented` | All tasks merged. Every criterion must have a test. | Engineer, in the last task |
| `Superseded` | Replaced by a later spec, which it links to. | Engineer |

## Conventions

- **Rules** are numbered `R1`, `R2`: single sentences that are always true.
- **Acceptance criteria** each get a heading `### AC-n: title` and are written
  as Given / When / Then with concrete values. Never renumber a criterion;
  if one is removed, retire its number.
- A criterion describes behaviour that can be observed from outside. It never
  names a class, a table or a library.
- Tests reference criteria with `@pytest.mark.covers("0001:AC-3")`.
  `make trace` checks that every criterion of an `Implemented` spec has a
  test, and that every reference points at a criterion that exists.
- Use the terms in [the glossary](../docs/domain/glossary.md).

## Changing a spec

An approved spec changes through a pull request, like code. Add a line to the
spec's change log. If the change alters behaviour, the same or the following
pull request changes the tests and the code.

The full process is in [docs/engineering/workflow.md](../docs/engineering/workflow.md).
