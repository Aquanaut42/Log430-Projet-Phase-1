# mongo_order_repository.py

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from domain.models.order import Order, OrderItem, OrderStatus
from domain.models.line import Line, LineStatus
from domain.exceptions.order_exceptions import OrderAlreadyExists
from application.ports.order_repository import OrderRepository

class MongoOrderRepository(OrderRepository):
    def __init__(self, mongo_uri: str):
        client = MongoClient(mongo_uri)
        db = client["cantelcox_order"]
        self.orders = db["orders"]
        self.lines = db["lines"]
        self.orders.create_index("idempotency_key", unique=True)
        self.lines.create_index("msisdn", unique=True)

    def save_order(self, order: Order) -> None:
        try:
            self.orders.insert_one({
                "_id": order.id,
                "customer_id": order.customer_id,
                "idempotency_key": order.idempotency_key,
                "status": order.status.value,
                "items": [
                    {
                        "plan_id": item.plan_id,
                        "plan_name": item.plan_name,
                        "price": item.price
                    }
                    for item in order.items
                ]
            })
        except DuplicateKeyError:
            raise OrderAlreadyExists("Commande déjà existante")

    def find_order_by_idempotency_key(self, key: str) -> Order | None:
        doc = self.orders.find_one({"idempotency_key": key})
        return self._to_order(doc) if doc else None

    def find_order_by_id(self, order_id: str) -> Order | None:
        doc = self.orders.find_one({"_id": order_id})
        return self._to_order(doc) if doc else None

    def update_order(self, order: Order) -> None:
        self.orders.update_one(
            {"_id": order.id},
            {"$set": {"status": order.status.value}}
        )

    def save_line(self, line: Line) -> None:
        self.lines.insert_one({
            "_id": line.id,
            "customer_id": line.customer_id,
            "msisdn": line.msisdn,
            "plan_id": line.plan_id,
            "status": line.status.value
        })

    def find_line_by_customer(self, customer_id: str) -> Line | None:
        doc = self.lines.find_one({"customer_id": customer_id})
        return self._to_line(doc) if doc else None

    def find_line_by_msisdn(self, msisdn: str) -> Line | None:
        doc = self.lines.find_one({"msisdn": msisdn})
        return self._to_line(doc) if doc else None

    def update_line(self, line: Line) -> None:
        self.lines.update_one(
            {"_id": line.id},
            {"$set": {"status": line.status.value}}
        )

    def _to_order(self, doc: dict) -> Order:
        return Order(
            id=doc["_id"],
            customer_id=doc["customer_id"],
            idempotency_key=doc["idempotency_key"],
            status=OrderStatus(doc["status"]),
            items=[
                OrderItem(
                    plan_id=item["plan_id"],
                    plan_name=item["plan_name"],
                    price=item["price"]
                )
                for item in doc.get("items", [])
            ]
        )

    def _to_line(self, doc: dict) -> Line:
        return Line(
            id=doc["_id"],
            customer_id=doc["customer_id"],
            msisdn=doc["msisdn"],
            plan_id=doc["plan_id"],
            status=LineStatus(doc["status"])
        )
