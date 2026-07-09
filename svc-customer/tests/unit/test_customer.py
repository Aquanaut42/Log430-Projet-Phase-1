# test_customer.py

import pytest
from domain.models.customer import Customer, CustomerStatus
from domain.models.otp import OTP
from domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists, CustomerNotFound, InvalidOTP
)

class TestCustomer:

    def test_customer_created_with_pending_status(self):
        customer = Customer(
            id="123",
            username="jchenier",
            password_hash="hash",
            nom="Jonathan",
            adresse="123 Rue Test",
            status=CustomerStatus.PENDING
        )
        assert customer.status == CustomerStatus.PENDING
        assert not customer.is_active()

    def test_customer_activate(self):
        customer = Customer(
            id="123",
            username="jchenier",
            password_hash="hash",
            nom="Jonathan",
            adresse="123 Rue Test",
            status=CustomerStatus.PENDING
        )
        customer.activate()
        assert customer.status == CustomerStatus.ACTIVE
        assert customer.is_active()

class TestOTP:

    def test_valid_otp(self):
        otp = OTP("123456")
        assert otp.is_valid()

    def test_invalid_otp(self):
        otp = OTP("000000")
        assert not otp.is_valid()

    def test_empty_otp(self):
        otp = OTP("")
        assert not otp.is_valid()
