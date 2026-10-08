# 0001: Layered architecture with enforced dependency rules

| Field | Value |
|---|---|
| Status | Accepted |
| Date | (date adopted) |
| Deciders | (team) |

## Context

The service encodes financial rules that outlive any framework or database
choice. The code is written and changed by several people and by AI agents,
so structure that relies on everyone remembering a convention will erode.

## Decision

The code is split into `domain`, `application`, `adapters`, `api` and `main`,
with dependencies pointing inwards only, as described in
[overview.md](../overview.md). The rules are checked by import-linter on every
commit and in CI.

`domain` and `application` do not import FastAPI, Pydantic, or any I/O library.
Domain objects are plain dataclasses; Pydantic models exist only in `api`.

## Alternatives considered

- **Routes that contain the logic.** Fewer files for small services. Rejected
  because rules end up duplicated across endpoints and can only be tested
  through HTTP.
- **Pydantic models as domain objects.** Less mapping code. Rejected because
  it ties business rules to the wire format: an API change would become a
  domain change, and the reverse.
- **The same layering by convention only.** Rejected because unenforced
  conventions decay, and faster when much of the code is generated.

## Consequences

- Business rules are tested in milliseconds without a server or database.
- Framework and database can be replaced without touching the rules.
- There is mapping code between API schemas and domain objects. This is
  deliberate: it is where the two are allowed to differ.
- A new contributor has one place to look for each kind of change.
