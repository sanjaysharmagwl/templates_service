# 0001: Refund a captured payment

| Field | Value |
|---|---|
| Status | Implemented |
| Owner | (name of the engineer accountable for this spec) |
| Approved by | (name of the product or domain owner, and date) |
| Plan | [plan.md](plan.md) |

> This spec is the worked example that ships with the template. It is complete
> and implemented, so you can follow one feature from requirement to code.

## Why

Operations staff need to return money to a payer after a payment has been
captured: a returned item, a duplicate charge, a goodwill gesture. Today there
is no way to do this through the service.

## Scope

In scope:

- Refunding part or all of a captured payment through the API.
- Protecting against refunding more than was captured.
- Safe retries, so a network failure never causes a double refund.

Out of scope:

- Sending the refund to a bank or card network (a later spec).
- Cancelling or reversing a refund.
- Authentication and authorisation (handled at the gateway today).

## Terms

Defined in [docs/domain/glossary.md](../../docs/domain/glossary.md): *payment*,
*captured amount*, *refund*, *refundable amount*, *idempotency key*.

## Behaviour

Callers send `POST /v1/payments/{payment_id}/refunds` with an `Idempotency-Key`
header and a body such as:

```json
{ "amount": { "value": "30.00", "currency": "INR" }, "reason": "Customer returned the item" }
```

`reason` is optional. A successful response is `201` with the refund: its `id`,
the `payment_id`, the `amount`, the `reason` and `requested_at`.

Every error response has a `code` that clients can branch on, a `message` for
humans, and `details` listing invalid fields when there are any.

### Rules

- **R1** The refunds on a payment never add up to more than its captured amount.
- **R2** A refund is in the currency the payment was captured in.
- **R3** A refund amount is greater than zero and has no more decimal places
  than its currency allows. Amounts are rejected, never rounded.
- **R4** The same idempotency key with the same amount and reason always yields
  the same refund. Keys are scoped to one payment.

## Acceptance criteria

In every example, payment `pay_1` was captured for 100.00 INR.

### AC-1: A partial refund is recorded

- **Given** nothing has been refunded on `pay_1`
- **When** a refund of 30.00 INR is requested
- **Then** the response is `201` with the refund
- **And** the refundable amount of `pay_1` is 70.00 INR

### AC-2: A payment can be refunded in parts, up to the captured amount

- **Given** 30.00 INR has been refunded on `pay_1`
- **When** a refund of 70.00 INR is requested with a new idempotency key
- **Then** the response is `201`
- **And** the refundable amount of `pay_1` is 0.00 INR

### AC-3: A refund larger than the refundable amount is rejected

- **Given** 30.00 INR has been refunded on `pay_1`
- **When** a refund of 70.01 INR is requested
- **Then** the response is `422` with code `refund_exceeds_refundable_amount`
- **And** no refund is recorded

### AC-4: A refund in another currency is rejected

- **When** a refund of 30.00 USD is requested on `pay_1`
- **Then** the response is `422` with code `currency_mismatch`
- **And** no refund is recorded

### AC-5: An amount that is not valid for the currency is rejected

- **When** a refund of 0.00 INR, or of 10.005 INR, is requested
- **Then** the response is `422` with code `invalid_amount`
- **And** no refund is recorded

### AC-6: A retried request returns the original refund

- **Given** a refund of 30.00 INR was accepted with idempotency key `K`
- **When** the same request is sent again with key `K`
- **Then** the response is `201` with the same refund as before
- **And** only one refund is recorded on `pay_1`

This holds even when nothing is left to refund.

### AC-7: Reusing a key for a different request is rejected

- **Given** a refund of 30.00 INR was accepted with idempotency key `K`
- **When** a request with key `K` and a different amount or reason is sent
- **Then** the response is `409` with code `idempotency_key_conflict`
- **And** only the original refund is recorded

### AC-8: A refund on an unknown payment is rejected

- **When** a refund is requested on a payment that does not exist
- **Then** the response is `404` with code `payment_not_found`

### AC-9: A malformed request is rejected without repeating its contents

- **When** the request has no idempotency key, an unknown field, an amount that
  is not a decimal string, or an unsupported currency
- **Then** the response is `422` with code `validation_error`
- **And** `details` names each invalid field
- **And** the response does not contain the rejected values

## Non-functional requirements

- **Money** is handled as exact decimals and sent as strings
  ([ADR 0002](../../docs/architecture/adr/0002-money-representation.md)).
- **Concurrency:** two simultaneous refunds on one payment must not break R1.
  The in-memory adapter does not guarantee this; the first database adapter
  must (see the note on `PaymentRepository`).
- **Privacy:** error responses and logs never contain rejected input values.

## Open questions

None. Questions raised during drafting, and their answers:

| Question | Answer | Decided by |
|---|---|---|
| Is exceeding the refundable amount a `409` or a `422`? | `422`: the request can never succeed as written, whereas `409` is kept for conflicts a client can resolve by changing the key. | (domain owner) |
| Should a retry return `200` instead of `201`? | No. A retry returns exactly what the first call returned, so clients need one code path. | (domain owner) |

## Change log

| Date | Change |
|---|---|
| (date) | Approved and implemented. |
