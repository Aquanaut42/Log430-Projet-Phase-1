# order.py

from enum import Enum
from dataclasses import dataclass, field
from typing import List

class OrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class OrderItem:
    plan_id: str
    plan_name: str
    price: float

@dataclass
class Order:
    id: str
    customer_id: str
    idempotency_key: str
    status: OrderStatus
    items: List[OrderItem] = field(default_factory=list)

    def complete(self):
        self.status = OrderStatus.COMPLETED

    def fail(self):
        self.status = OrderStatus.FAILED

    def is_completed(self) -> bool:
        return self.status == OrderStatus.COMPLETED
