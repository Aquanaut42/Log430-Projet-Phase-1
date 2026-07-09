# place_order.py

import uuid
import requests
import os
from domain.models.order import Order, OrderItem, OrderStatus
from domain.exceptions.order_exceptions import (
    OrderAlreadyExists, CustomerNotActive
)
from application.ports.order_repository import OrderRepository

PLANS = {
    "plan-basic": {"name": "Forfait Basic", "price": 35.00},
    "plan-standard": {"name": "Forfait Standard", "price": 55.00},
    "plan-premium": {"name": "Forfait Premium", "price": 75.00},
}

class PlaceOrder:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def execute(self, customer_id: str, plan_id: str,
                idempotency_key: str) -> Order:

        existing = self.repository.find_order_by_idempotency_key(
            idempotency_key
        )
        if existing:
            return existing

        self._verify_customer_active(customer_id)

        if plan_id not in PLANS:
            raise ValueError(f"Forfait {plan_id} introuvable")

        plan = PLANS[plan_id]

        order = Order(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            idempotency_key=idempotency_key,
            status=OrderStatus.COMPLETED,
            items=[OrderItem(
                plan_id=plan_id,
                plan_name=plan["name"],
                price=plan["price"]
            )]
        )

        self.repository.save_order(order)
        return order

    def _verify_customer_active(self, customer_id: str):

        customer_url = os.getenv("CUSTOMER_SERVICE_URL")
        try:
            response = requests.get(
                f"{customer_url}/v1/customers/{customer_id}",
                timeout=5
            )
            if response.status_code == 404:
                raise CustomerNotActive("Client introuvable")
            data = response.json()
            if data.get("status") != "active":
                raise CustomerNotActive("Le profil abonné n'est pas actif")
        except requests.exceptions.ConnectionError:
            raise CustomerNotActive("Service client indisponible")
