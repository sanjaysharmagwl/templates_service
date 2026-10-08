"""Run the service locally with sample data, to try the API by hand.

Run it with `make run`, then open http://127.0.0.1:8000/docs. One payment
exists, `pay_demo`, captured for 100.00 INR. Data lives in memory and is lost
when the server stops.
"""

from decimal import Decimal

import uvicorn

from service_template.adapters.in_memory import InMemoryPaymentRepository
from service_template.domain.money import Currency, Money
from service_template.domain.payment import Payment, PaymentId
from service_template.main import create_app


def main() -> None:
    payments = InMemoryPaymentRepository()
    payments.save(
        Payment(id=PaymentId("pay_demo"), captured=Money(Decimal("100.00"), Currency.INR))
    )
    uvicorn.run(create_app(payments), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
