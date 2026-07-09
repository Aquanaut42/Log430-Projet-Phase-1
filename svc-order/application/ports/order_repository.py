# order_repository.py

from abc import ABC, abstractmethod
from domain.models.order import Order
from domain.models.line import Line

class OrderRepository(ABC):

    @abstractmethod
    def save_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_order_by_idempotency_key(self, key: str) -> Order | None:
        pass

    @abstractmethod
    def find_order_by_id(self, order_id: str) -> Order | None:
        pass

    @abstractmethod
    def update_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def save_line(self, line: Line) -> None:
        pass

    @abstractmethod
    def find_line_by_customer(self, customer_id: str) -> Line | None:
        pass

    @abstractmethod
    def find_line_by_msisdn(self, msisdn: str) -> Line | None:
        pass

    @abstractmethod
    def update_line(self, line: Line) -> None:
        pass
