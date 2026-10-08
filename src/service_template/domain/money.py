"""Money and currency value objects.

Money is an exact decimal amount in one currency. Floats never represent money
anywhere in this service, and amounts are rejected rather than rounded
(docs/architecture/adr/0002-money-representation.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from service_template.domain.errors import CurrencyMismatchError, InvalidAmountError


class Currency(StrEnum):
    """ISO 4217 currencies this service accepts."""

    EUR = "EUR"
    INR = "INR"
    JPY = "JPY"
    USD = "USD"

    @property
    def minor_units(self) -> int:
        """Decimal places the currency allows (its ISO 4217 exponent)."""
        return _MINOR_UNITS[self]


_MINOR_UNITS = {
    Currency.EUR: 2,
    Currency.INR: 2,
    Currency.JPY: 0,
    Currency.USD: 2,
}


@dataclass(frozen=True, slots=True)
class Money:
    """A non-negative amount in a single currency.

    Amounts are never negative here: a refund is a positive amount flowing in
    the opposite direction, not a negative payment.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if _decimal_places(self.amount) > self.currency.minor_units:
            raise InvalidAmountError(
                f"{self.currency} amounts allow at most {self.currency.minor_units} decimal places"
            )
        if self.amount < 0:
            raise InvalidAmountError("amount must not be negative")

    @classmethod
    def zero(cls, currency: Currency) -> Money:
        return cls(Decimal(0), currency)

    @property
    def is_zero(self) -> bool:
        return self.amount == 0

    def __add__(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def _require_same_currency(self, other: Money) -> None:
        if other.currency != self.currency:
            raise CurrencyMismatchError(f"cannot combine {self.currency} with {other.currency}")


def _decimal_places(value: Decimal) -> int:
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):  # NaN and infinity have no exponent
        raise InvalidAmountError("amount must be a finite number")
    return max(-exponent, 0)
