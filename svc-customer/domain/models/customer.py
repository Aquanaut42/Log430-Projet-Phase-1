# customer.py

from enum import Enum
from dataclasses import dataclass

class CustomerStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"

@dataclass
class Customer:
    id: str
    username: str
    password_hash: str
    nom: str
    adresse: str
    status: CustomerStatus = CustomerStatus.PENDING

    def activate(self):
        self.status = CustomerStatus.ACTIVE

    def is_active(self) -> bool:
        return self.status == CustomerStatus.ACTIVE
