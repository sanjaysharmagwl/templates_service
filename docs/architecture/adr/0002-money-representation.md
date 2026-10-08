# 0002: Money is an exact decimal with a currency, and is never rounded silently

| Field | Value |
|---|---|
| Status | Accepted |
| Date | (date adopted) |
| Deciders | (team) |

## Context

Binary floating point cannot represent most decimal fractions exactly:
`0.1 + 0.2` is not `0.3`. In financial code this produces amounts that are off
by a minor unit, and totals that do not reconcile. JSON numbers have the same
problem in many clients, which parse them as floats.

Currencies also differ in how many decimal places they allow: two for INR and
USD, none for JPY, three for some others.

## Decision

- Inside the service, money is the `Money` value object: a `Decimal` amount
  and a `Currency`. `float` is never used for an amount.
- `Money` refuses an amount with more decimal places than its currency allows.
  The service does not round. A feature that needs rounding (interest, fees,
  currency conversion) must name the rounding mode in its spec.
- Arithmetic and comparison between different currencies is an error.
- In the API, an amount is an object with a decimal string and a currency
  code: `{"value": "25.00", "currency": "INR"}`.

## Alternatives considered

- **Integers in minor units** (`2500` for 25.00 INR). Exact and compact, and a
  reasonable choice. Not chosen because the meaning of the number depends on
  the currency, which makes logs and payloads easy to misread, and because
  some calculations need more precision than the minor unit.
- **JSON numbers.** Rejected: clients routinely parse them as floats.
- **Round to the currency's precision on input.** Rejected: it hides client
  errors and changes amounts without anyone deciding to.

## Consequences

- Amounts reconcile exactly.
- Clients must send strings; a JSON number is rejected by validation.
- Supporting a new currency means adding it to `Currency` with its minor units.
- Database adapters must store amounts in an exact type (`NUMERIC`), never a
  floating-point column.
