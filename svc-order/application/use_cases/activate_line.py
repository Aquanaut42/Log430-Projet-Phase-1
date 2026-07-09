# activate_line.py

import uuid
import random
from domain.models.line import Line, LineStatus
from domain.exceptions.order_exceptions import (
    LineAlreadyExists, CustomerNotActive
)
from application.ports.order_repository import OrderRepository

class ActivateLine:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def execute(self, customer_id: str, plan_id: str) -> Line:

        existing = self.repository.find_line_by_customer(customer_id)
        if existing and existing.is_active():
            raise LineAlreadyExists("Ce client a déjà une ligne active")

        msisdn = self._generate_msisdn()

        line = Line(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            msisdn=msisdn,
            plan_id=plan_id,
            status=LineStatus.ACTIVE
        )

        self.repository.save_line(line)
        return line

    def _generate_msisdn(self) -> str:

        number = random.randint(1000000, 9999999)
        return f"+1514{number}"
