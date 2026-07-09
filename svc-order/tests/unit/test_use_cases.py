# test_use_cases.py

import pytest
from unittest.mock import MagicMock, patch
from application.use_cases.place_order import PlaceOrder
from application.use_cases.activate_line import ActivateLine
from application.use_cases.get_usage import GetUsage
from domain.models.order import Order, OrderStatus
from domain.models.line import Line, LineStatus
from domain.exceptions.order_exceptions import (
    OrderAlreadyExists, CustomerNotActive,
    LineAlreadyExists, LineNotFound
)

class TestPlaceOrder:

    def test_place_order_success(self):
        repo = MagicMock()
        repo.find_order_by_idempotency_key.return_value = None

        with patch("application.use_cases.place_order.PlaceOrder._verify_customer_active"):
            use_case = PlaceOrder(repo)
            order = use_case.execute(
                customer_id="cust-123",
                plan_id="plan-basic",
                idempotency_key="key-001"
            )

        assert order.status == OrderStatus.COMPLETED
        assert order.items[0].plan_id == "plan-basic"
        repo.save_order.assert_called_once()

    def test_place_order_idempotent(self):
        existing_order = Order(
            id="ord-existing",
            customer_id="cust-123",
            idempotency_key="key-001",
            status=OrderStatus.COMPLETED,
            items=[]
        )
        repo = MagicMock()
        repo.find_order_by_idempotency_key.return_value = existing_order

        use_case = PlaceOrder(repo)
        order = use_case.execute(
            customer_id="cust-123",
            plan_id="plan-basic",
            idempotency_key="key-001"
        )

        assert order.id == "ord-existing"
        repo.save_order.assert_not_called()

    def test_place_order_invalid_plan(self):
        repo = MagicMock()
        repo.find_order_by_idempotency_key.return_value = None

        with patch("application.use_cases.place_order.PlaceOrder._verify_customer_active"):
            use_case = PlaceOrder(repo)
            with pytest.raises(ValueError):
                use_case.execute(
                    customer_id="cust-123",
                    plan_id="plan-inexistant",
                    idempotency_key="key-002"
                )

class TestActivateLine:

    def test_activate_line_success(self):
        repo = MagicMock()
        repo.find_line_by_customer.return_value = None

        use_case = ActivateLine(repo)
        line = use_case.execute(
            customer_id="cust-123",
            plan_id="plan-basic"
        )

        assert line.is_active()
        assert line.msisdn.startswith("+1514")
        repo.save_line.assert_called_once()

    def test_activate_line_already_exists(self):
        existing_line = Line(
            id="line-123",
            customer_id="cust-123",
            msisdn="+15141234567",
            plan_id="plan-basic",
            status=LineStatus.ACTIVE
        )
        repo = MagicMock()
        repo.find_line_by_customer.return_value = existing_line

        use_case = ActivateLine(repo)
        with pytest.raises(LineAlreadyExists):
            use_case.execute(
                customer_id="cust-123",
                plan_id="plan-basic"
            )

        repo.save_line.assert_not_called()

class TestGetUsage:

    def test_get_usage_success(self):
        line = Line(
            id="line-123",
            customer_id="cust-123",
            msisdn="+15141234567",
            plan_id="plan-basic",
            status=LineStatus.ACTIVE
        )
        repo = MagicMock()
        repo.find_line_by_customer.return_value = line

        with patch("application.use_cases.get_usage.GetUsage._fetch_usage",
                   return_value={"voix_minutes": 45, "sms": 120}):
            use_case = GetUsage(repo)
            result = use_case.execute("cust-123")

        assert result["msisdn"] == "+15141234567"
        assert result["plan_id"] == "plan-basic"
        assert "usage" in result

    def test_get_usage_no_line(self):
        repo = MagicMock()
        repo.find_line_by_customer.return_value = None

        use_case = GetUsage(repo)
        with pytest.raises(LineNotFound):
            use_case.execute("cust-123")
