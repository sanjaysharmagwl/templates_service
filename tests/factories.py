"""Small builders that keep test setup readable."""

from decimal import Decimal

from service_template.domain.money import Currency, Money
from service_template.domain.payment import Payment, PaymentId


def inr(value: str) -> Money:
    return Money(Decimal(value), Currency.INR)


def usd(value: str) -> Money:
    return Money(Decimal(value), Currency.USD)


def captured_payment(payment_id: str, captured: Money) -> Payment:
    return Payment(id=PaymentId(payment_id), captured=captured)
