"""In-memory adapters, used by the tests and the local dev server.

They stand in for a real database. Replace them in `main.create_app` when the
service gets its first persistent adapter.
"""

import copy

from service_template.domain.payment import Payment, PaymentId


class InMemoryPaymentRepository:
    """Keeps payments in a dict.

    Payments are copied on the way in and out, as a database would do, so a
    use case that forgets to call `save` fails its tests instead of passing by
    accident. Not safe for concurrent writers.
    """

    def __init__(self) -> None:
        self._payments: dict[PaymentId, Payment] = {}

    def get(self, payment_id: PaymentId) -> Payment | None:
        payment = self._payments.get(payment_id)
        return copy.deepcopy(payment)

    def save(self, payment: Payment) -> None:
        self._payments[payment.id] = copy.deepcopy(payment)
