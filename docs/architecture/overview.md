# Architecture

The service is organised in layers. Business rules sit in the middle and know
nothing about HTTP or databases; everything else depends on them.

```
            ┌──────────────────────────────────────────┐
            │ main        wires everything together    │
            └────────────┬───────────────┬─────────────┘
                         │               │
            ┌────────────▼────┐   ┌──────▼────────────┐
            │ api             │   │ adapters          │
            │ HTTP, schemas,  │   │ database, clock,  │
            │ error mapping   │   │ other services    │
            └────────────┬────┘   └──────┬────────────┘
                         │               │
            ┌────────────▼───────────────▼─────────────┐
            │ application   use cases and ports        │
            └────────────────────┬─────────────────────┘
                                 │
            ┌────────────────────▼─────────────────────┐
            │ domain        business rules             │
            └──────────────────────────────────────────┘
```

Arrows show which layer may import which. They only point down.

| Layer | Contains | May import |
|---|---|---|
| `domain` | Entities, value objects, business rules, domain errors | The standard library |
| `application` | Use cases; ports (interfaces for what a use case needs) | `domain` |
| `adapters` | Implementations of ports | `application`, `domain`, I/O libraries |
| `api` | Routes, request and response schemas, error mapping | `application`, `domain`, FastAPI, Pydantic |
| `main` | `create_app`: builds adapters and use cases, registers routes | Everything |

`api` and `adapters` do not import each other.

These rules are enforced by import-linter (`make arch`), configured in
`pyproject.toml`. The reasoning is in [ADR 0001](adr/0001-layered-architecture.md).

## How a request flows

`POST /v1/payments/{payment_id}/refunds`:

1. `api/refunds.py` validates the request against the schema and builds a
   `RequestRefundCommand` from domain types.
2. `application/request_refund.py` loads the `Payment` through the
   `PaymentRepository` port.
3. `domain/payment.py` applies the rules in `Payment.request_refund` and
   either records the refund or raises a `DomainError`.
4. The use case saves the payment and returns the refund.
5. `api` converts the refund to a response, or `api/errors.py` converts the
   error to an `ErrorResponse`.

## Where does new code go?

| You are adding | Put it in |
|---|---|
| A business rule or calculation | `domain`, on the object that owns the data |
| A new operation the service can perform | A use case in `application` |
| Something the use case needs from outside (storage, another service, time) | A port in `application/ports.py`, an implementation in `adapters` |
| An endpoint | A route in `api`, schemas in `api/schemas.py` |
| A mapping from an error to an HTTP status | `api/errors.py` |
| Construction and configuration | `main.py` |

If a rule seems to belong in `api` or `adapters`, it does not. Move it inwards.

## Decisions still to make

The template leaves these open because they depend on your environment. Record
each one as an ADR when you make it.

- **Persistence.** The in-memory repository is a stand-in. The first real
  adapter must make concurrent refunds on one payment safe, with a row lock or
  a version check.
- **Sync or async.** Ports and routes are synchronous. If you choose an async
  database driver, change the ports to `async def` before writing the first
  real adapter; changing it later touches every use case.
- **Transactions.** A use case is one unit of work. Decide how adapters share
  a transaction when a use case writes through more than one port.
- **Authentication and authorisation.**
- **Audit trail and structured logging.**
- **Configuration and secrets.**

## Decision records

Significant decisions are recorded in [adr/](adr/), one file each, using
[the template](adr/0000-template.md). An ADR is short: the context, the
decision, and what follows from it. They are never edited after acceptance;
a later decision supersedes an earlier one.
