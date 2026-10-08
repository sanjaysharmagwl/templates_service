# Glossary

The words this team uses, each with one meaning. Use exactly these terms in
specs, code, tests and conversation. When a spec needs a new term, add it here
in the same pull request.

| Term | Meaning | In code |
|---|---|---|
| **Payment** | Money taken from a payer for one purchase. | `Payment` |
| **Captured amount** | The money actually taken for a payment. It never changes after capture. | `Payment.captured` |
| **Refund** | Money returned to the payer from one payment. Always a positive amount. | `Refund` |
| **Refunded amount** | The total of all refunds on a payment. | `Payment.refunded` |
| **Refundable amount** | What can still be refunded: captured amount minus refunded amount. | `Payment.refundable` |
| **Money** | An exact decimal amount together with its currency. | `Money` |
| **Minor units** | The number of decimal places a currency uses: 2 for INR, 0 for JPY. | `Currency.minor_units` |
| **Idempotency key** | A value the client chooses to identify one request, so that sending it again returns the first result instead of repeating the action. | `Refund.idempotency_key` |

## Words we avoid

| Do not say | Because | Say instead |
|---|---|---|
| Balance | It means different things for a payment, an account and a ledger. | Refundable amount, or the specific term |
| Transaction | It is used for payments, refunds and database transactions alike. | Payment or refund |
| Reversal | It suggests the payment is undone. A refund is a new movement of money. | Refund |
