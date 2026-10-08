"""Ports: what the use cases need from the outside world.

Adapters implement these. Use cases depend only on the interfaces here, which
is what lets the tests run against in-memory implementations.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Protocol

from service_template.domain.payment import Payment, PaymentId, RefundId

Clock = Callable[[], datetime]
"""Returns the current time as a timezone-aware UTC datetime."""

RefundIdFactory = Callable[[], RefundId]
"""Returns a new, unique refund identifier."""


class PaymentRepository(Protocol):
    """Loads and stores payments.

    Implementations backed by a real database must make sure two refunds on
    the same payment cannot be saved concurrently (row lock or version check),
    otherwise the payment could be refunded for more than was captured.
    """

    def get(self, payment_id: PaymentId) -> Payment | None: ...

    def save(self, payment: Payment) -> None: ...
