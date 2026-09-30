from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel


OrderStatusValue = Literal[
    "PENDING",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED",
]


class OrderStatus(BaseModel):
    order_number: str
    user_id: str
    status: OrderStatusValue
    changed_at: datetime


class OrderStatusList(BaseModel):
    items: List[OrderStatus]
    total: int
    limit: int
    offset: int