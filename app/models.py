from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    MetaData,
    Table,
    UniqueConstraint,
)
from sqlalchemy.types import Unicode


STATUS_VALUES = (
    "PENDING",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED",
)

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("order_number", Unicode(50), nullable=False, unique=True),
    Column("user_id", Unicode(100), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("IX_orders_user_id", "user_id"),
)

order_status_history = Table(
    "order_status_history",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column(
        "order_id",
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("status", Unicode(20), nullable=False),
    Column("changed_at", DateTime(timezone=True), nullable=False),
    Column("note", Unicode(500)),
    CheckConstraint(
        "status IN ('PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')",
        name="CK_order_status_history_status",
    ),
    UniqueConstraint("order_id", "changed_at", name="UQ_order_status_changed_at"),
    Index("IX_order_status_history_order_changed", "order_id", "changed_at"),
    Index("IX_order_status_history_changed_at", "changed_at"),
)