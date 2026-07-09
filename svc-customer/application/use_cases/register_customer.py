# register_customer.py

import uuid
import hashlib
from domain.models.customer import Customer, CustomerStatus
from domain.exceptions.customer_exceptions import CustomerAlreadyExists
from application.ports.customer_repository import CustomerRepository

class RegisterCustomer:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def execute(self, username: str, password: str,
                nom: str, adresse: str) -> Customer:

        existing = self.repository.find_by_username(username)
        if existing:
            raise CustomerAlreadyExists(f"Username {username} déjà utilisé")

        customer = Customer(
            id=str(uuid.uuid4()),
            username=username,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            nom=nom,
            adresse=adresse,
            status=CustomerStatus.PENDING
        )

        self.repository.save(customer)
        return customer
