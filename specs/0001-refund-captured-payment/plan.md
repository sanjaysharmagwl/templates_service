# Plan for 0001: Refund a captured payment

The spec says *what*. This plan says *how*, and breaks the work into tasks
small enough to review one at a time.

## Approach

`Payment` is the aggregate that owns refunds, so the rules R1 to R4 live in one
method, `Payment.request_refund`. Idempotency is checked there too: each refund
stores the key it was created with, which keeps the key and the refund in the
same transaction and needs no separate idempotency store.

| Layer | Change |
|---|---|
| domain | `Money`, `Currency`, `Payment`, `Refund`, and the errors for R1 to R4 |
| application | `RequestRefund` use case; `PaymentRepository` port |
| adapters | `InMemoryPaymentRepository`; system clock and id generator |
| api | `POST /v1/payments/{payment_id}/refunds`; error mapping |

## Contract

One new operation, `requestRefund`. Responses: `201`, `400`, `404`, `409`,
`422`. All errors use `ErrorResponse`. No existing operation changes.

## Test plan

| Criterion | Unit (domain) | Acceptance (HTTP) |
|---|---|---|
| AC-1 to AC-7 | `tests/unit/test_payment.py` | `tests/acceptance/test_0001_refund_captured_payment.py` |
| AC-8 | `tests/unit/test_request_refund.py` | same acceptance file |
| AC-9 | not applicable: enforced by the request schema | same acceptance file |
| R1, R4 for any sequence of requests | `tests/unit/test_payment_properties.py` | |
| Contract conformance | | `tests/contract/` |

## Tasks

Each task is one pull request that leaves `make check` green.

- [x] 1. Contract: request and response schemas, route stub, `contracts/openapi.json`
- [x] 2. Domain: `Money` and `Currency` with tests
- [x] 3. Domain: `Payment.request_refund` with unit and property tests (R1 to R4)
- [x] 4. Application: `RequestRefund` and the repository port, with tests
- [x] 5. API: wire the route to the use case; acceptance tests for AC-1 to AC-9
- [x] 6. Set the spec status to Implemented

## Risks

- **Concurrent refunds.** Not solved by the in-memory adapter. Tracked in the
  spec's non-functional requirements; must be addressed with the first
  database adapter.
