# line.py

from enum import Enum
from dataclasses import dataclass

class LineStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"

@dataclass
class Line:
    id: str
    customer_id: str
    msisdn: str
    plan_id: str
    status: LineStatus = LineStatus.PENDING

    def activate(self):
        self.status = LineStatus.ACTIVE

    def is_active(self) -> bool:
        return self.status == LineStatus.ACTIVE
