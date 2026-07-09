# customer_repository.py

from abc import ABC, abstractmethod
from domain.models.customer import Customer

class CustomerRepository(ABC):

    @abstractmethod
    def save(self, customer: Customer) -> None:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Customer | None:
        pass

    @abstractmethod
    def find_by_id(self, customer_id: str) -> Customer | None:
        pass

    @abstractmethod
    def update(self, customer: Customer) -> None:
        pass
