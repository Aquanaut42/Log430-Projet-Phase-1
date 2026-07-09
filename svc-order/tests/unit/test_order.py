# test_order.py

import pytest
from domain.models.order import Order, OrderItem, OrderStatus
from domain.models.line import Line, LineStatus

class TestOrder:

    def make_order(self):
        return Order(
            id="ord-123",
            customer_id="cust-123",
            idempotency_key="key-001",
            status=OrderStatus.PENDING,
            items=[OrderItem(
                plan_id="plan-basic",
                plan_name="Forfait Basic",
                price=35.0
            )]
        )

    def test_order_created_pending(self):
        order = self.make_order()
        assert order.status == OrderStatus.PENDING
        assert not order.is_completed()

    def test_order_complete(self):
        order = self.make_order()
        order.complete()
        assert order.status == OrderStatus.COMPLETED
        assert order.is_completed()

    def test_order_fail(self):
        order = self.make_order()
        order.fail()
        assert order.status == OrderStatus.FAILED
        assert not order.is_completed()

class TestLine:

    def make_line(self):
        return Line(
            id="line-123",
            customer_id="cust-123",
            msisdn="+15141234567",
            plan_id="plan-basic",
            status=LineStatus.PENDING
        )

    def test_line_created_pending(self):
        line = self.make_line()
        assert line.status == LineStatus.PENDING
        assert not line.is_active()

    def test_line_activate(self):
        line = self.make_line()
        line.activate()
        assert line.status == LineStatus.ACTIVE
        assert line.is_active()
