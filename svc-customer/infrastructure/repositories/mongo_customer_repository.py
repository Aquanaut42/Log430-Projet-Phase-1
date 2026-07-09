# mongo_customer_repository.py

from pymongo import MongoClient
from domain.models.customer import Customer, CustomerStatus
from application.ports.customer_repository import CustomerRepository

class MongoCustomerRepository(CustomerRepository):
    def __init__(self, mongo_uri: str):
        client = MongoClient(mongo_uri)
        self.collection = client["cantelcox"]["customers"]

    def save(self, customer: Customer) -> None:
        self.collection.insert_one({
            "_id": customer.id,
            "username": customer.username,
            "password_hash": customer.password_hash,
            "nom": customer.nom,
            "adresse": customer.adresse,
            "status": customer.status.value
        })

    def find_by_username(self, username: str) -> Customer | None:
        doc = self.collection.find_one({"username": username})
        return self._to_customer(doc) if doc else None

    def find_by_id(self, customer_id: str) -> Customer | None:
        doc = self.collection.find_one({"_id": customer_id})
        return self._to_customer(doc) if doc else None

    def update(self, customer: Customer) -> None:
        self.collection.update_one(
            {"_id": customer.id},
            {"$set": {"status": customer.status.value}}
        )

    def _to_customer(self, doc: dict) -> Customer:
        return Customer(
            id=doc["_id"],
            username=doc["username"],
            password_hash=doc["password_hash"],
            nom=doc["nom"],
            adresse=doc["adresse"],
            status=CustomerStatus(doc["status"])
        )
