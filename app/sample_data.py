from datetime import datetime, timezone

from sqlalchemy import insert, select
from sqlalchemy.engine import Connection

from app.models import order_status_history, orders


SAMPLE_ORDERS = (
    ("ORD-1001", "USER-101", "2026-06-01T08:55:00Z"),
    ("ORD-1002", "USER-101", "2026-06-03T14:10:00Z"),
    ("ORD-1003", "USER-202", "2026-06-02T11:20:00Z"),
    ("ORD-1004", "USER-303", "2026-06-05T09:00:00Z"),
)

SAMPLE_STATUSES = (
    ("ORD-1001", "PENDING", "2026-06-01T09:00:00Z", "Order placed"),
    ("ORD-1001", "PROCESSING", "2026-06-01T10:30:00Z", "Payment confirmed"),
    ("ORD-1001", "SHIPPED", "2026-06-02T12:00:00Z", "Carrier pickup"),
    ("ORD-1001", "DELIVERED", "2026-06-04T16:45:00Z", "Delivered to recipient"),
    ("ORD-1002", "PENDING", "2026-06-03T14:10:00Z", "Order placed"),
    ("ORD-1002", "PROCESSING", "2026-06-03T15:00:00Z", "Payment confirmed"),
    ("ORD-1002", "CANCELLED", "2026-06-04T08:15:00Z", "Cancelled by customer"),
    ("ORD-1003", "PENDING", "2026-06-02T11:25:00Z", "Order placed"),
    ("ORD-1003", "PROCESSING", "2026-06-02T13:40:00Z", "Payment confirmed"),
    ("ORD-1003", "SHIPPED", "2026-06-03T09:00:00Z", "Carrier pickup"),
    ("ORD-1004", "PENDING", "2026-06-05T09:05:00Z", "Order placed"),
    ("ORD-1004", "PROCESSING", "2026-06-05T10:00:00Z", "Payment confirmed"),
)


def _utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def seed_sample_data(connection: Connection) -> None:
    for order_number, user_id, created_at in SAMPLE_ORDERS:
        order_id = connection.execute(
            select(orders.c.id).where(orders.c.order_number == order_number)
        ).scalar_one_or_none()
        if order_id is None:
            connection.execute(
                insert(orders).values(
                    order_number=order_number,
                    user_id=user_id,
                    created_at=_utc_datetime(created_at),
                )
            )

    for order_number, status, changed_at, note in SAMPLE_STATUSES:
        order_id = connection.execute(
            select(orders.c.id).where(orders.c.order_number == order_number)
        ).scalar_one()
        timestamp = _utc_datetime(changed_at)
        existing = connection.execute(
            select(order_status_history.c.id).where(
                order_status_history.c.order_id == order_id,
                order_status_history.c.changed_at == timestamp,
            )
        ).scalar_one_or_none()
        if existing is None:
            connection.execute(
                insert(order_status_history).values(
                    order_id=order_id,
                    status=status,
                    changed_at=timestamp,
                    note=note,
                )
            )