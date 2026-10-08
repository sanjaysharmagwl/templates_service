"""Adapters for things the operating system provides: time and randomness."""

from datetime import UTC, datetime
from uuid import uuid4

from service_template.domain.payment import RefundId


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_refund_id() -> RefundId:
    return RefundId(f"rf_{uuid4().hex}")
