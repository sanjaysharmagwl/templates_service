from decimal import Decimal

import pytest

from service_template.domain.errors import CurrencyMismatchError, InvalidAmountError
from service_template.domain.money import Currency, Money
from tests.factories import inr, usd


@pytest.mark.parametrize(
    ("value", "currency"),
    [
        ("0", Currency.INR),
        ("10", Currency.INR),
        ("10.5", Currency.INR),
        ("10.50", Currency.USD),
        ("1500", Currency.JPY),
    ],
)
def test_amount_within_the_currency_precision_is_accepted(value: str, currency: Currency) -> None:
    money = Money(Decimal(value), currency)

    assert money.amount == Decimal(value)


@pytest.mark.parametrize(
    ("value", "currency"),
    [
        ("10.001", Currency.INR),
        ("10.500", Currency.USD),
        ("1500.5", Currency.JPY),
    ],
)
def test_amount_with_too_many_decimal_places_is_rejected(value: str, currency: Currency) -> None:
    with pytest.raises(InvalidAmountError, match="decimal places"):
        Money(Decimal(value), currency)


def test_negative_amount_is_rejected() -> None:
    with pytest.raises(InvalidAmountError, match="negative"):
        inr("-0.01")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_amount_that_is_not_a_finite_number_is_rejected(value: str) -> None:
    with pytest.raises(InvalidAmountError, match="finite"):
        inr(value)


def test_amounts_in_the_same_currency_add_and_subtract_exactly() -> None:
    assert inr("0.10") + inr("0.20") == inr("0.30")
    assert inr("100.00") - inr("0.01") == inr("99.99")


def test_subtracting_more_than_is_there_is_rejected() -> None:
    with pytest.raises(InvalidAmountError):
        inr("1.00") - inr("1.01")


def test_amounts_in_different_currencies_cannot_be_combined() -> None:
    with pytest.raises(CurrencyMismatchError):
        inr("1.00") + usd("1.00")
    with pytest.raises(CurrencyMismatchError):
        inr("1.00") - usd("1.00")


def test_trailing_zeros_do_not_change_the_value() -> None:
    assert inr("10.5") == inr("10.50")


def test_same_number_in_another_currency_is_different_money() -> None:
    assert inr("10.00") != usd("10.00")


def test_money_reads_as_amount_and_currency() -> None:
    assert str(inr("10.50")) == "10.50 INR"
