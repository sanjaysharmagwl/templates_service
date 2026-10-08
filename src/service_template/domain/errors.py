"""Business-rule violations.

Each error is a rule from a spec that the caller broke. The messages are shown
to API clients, so they describe the rule and never include internal details.
"""


class DomainError(Exception):
    """Base class for every business-rule violation."""


class InvalidAmountError(DomainError):
    """The amount is not a valid sum of money in its currency."""


class CurrencyMismatchError(DomainError):
    """Two amounts in different currencies were combined or compared."""


class RefundExceedsRefundableAmountError(DomainError):
    """The refund is larger than what is left to refund on the payment."""


class IdempotencyKeyConflictError(DomainError):
    """An idempotency key was reused for a different request."""
