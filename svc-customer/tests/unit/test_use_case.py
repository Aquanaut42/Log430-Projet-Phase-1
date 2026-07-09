# test_use_case.py

import pytest
from unittest.mock import MagicMock
from application.use_cases.register_customer import RegisterCustomer
from application.use_cases.authenticate_mfa import AuthenticateMFA
from domain.models.customer import Customer, CustomerStatus
from domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists, CustomerNotFound, InvalidOTP
)

def make_customer(status=CustomerStatus.PENDING):
    return Customer(
        id="123",
        username="jchenier",
        password_hash="ef92b778bafe771207b9f...",  # hash simulé
        nom="Jonathan",
        adresse="123 Rue Test",
        status=status
    )

class TestRegisterCustomer:

    def test_register_new_customer(self):
        repo = MagicMock()
        repo.find_by_username.return_value = None

        use_case = RegisterCustomer(repo)
        customer = use_case.execute(
            username="jchenier",
            password="motdepasse123",
            nom="Jonathan",
            adresse="123 Rue Test"
        )

        assert customer.status == CustomerStatus.PENDING
        assert customer.username == "jchenier"
        repo.save.assert_called_once()

    def test_register_duplicate_username(self):
        repo = MagicMock()
        repo.find_by_username.return_value = make_customer()

        use_case = RegisterCustomer(repo)
        with pytest.raises(CustomerAlreadyExists):
            use_case.execute(
                username="jchenier",
                password="motdepasse123",
                nom="Jonathan",
                adresse="123 Rue Test"
            )

        repo.save.assert_not_called()

class TestAuthenticateMFA:

    def test_verify_credentials_success(self):
        import hashlib
        password = "motdepasse123"
        hashed = hashlib.sha256(password.encode()).hexdigest()

        customer = make_customer()
        customer.password_hash = hashed

        repo = MagicMock()
        repo.find_by_username.return_value = customer

        use_case = AuthenticateMFA(repo)
        customer_id = use_case.verify_credentials("jchenier", password)

        assert customer_id == "123"

    def test_verify_credentials_wrong_password(self):
        import hashlib
        customer = make_customer()
        customer.password_hash = hashlib.sha256(b"bon_mot_de_passe").hexdigest()

        repo = MagicMock()
        repo.find_by_username.return_value = customer

        use_case = AuthenticateMFA(repo)
        with pytest.raises(InvalidOTP):
            use_case.verify_credentials("jchenier", "mauvais_mot_de_passe")

    def test_verify_credentials_user_not_found(self):
        repo = MagicMock()
        repo.find_by_username.return_value = None

        use_case = AuthenticateMFA(repo)
        with pytest.raises(CustomerNotFound):
            use_case.verify_credentials("inconnu", "motdepasse")

    def test_verify_otp_valid(self):
        repo = MagicMock()
        repo.find_by_id.return_value = make_customer()

        use_case = AuthenticateMFA(repo)
        customer = use_case.verify_otp_and_activate("123", "123456")

        assert customer.is_active()
        repo.update.assert_called_once()

    def test_verify_otp_invalid(self):
        repo = MagicMock()
        repo.find_by_id.return_value = make_customer()

        use_case = AuthenticateMFA(repo)
        with pytest.raises(InvalidOTP):
            use_case.verify_otp_and_activate("123", "000000")

        repo.update.assert_not_called()

    def test_verify_otp_customer_not_found(self):
        repo = MagicMock()
        repo.find_by_id.return_value = None

        use_case = AuthenticateMFA(repo)
        with pytest.raises(CustomerNotFound):
            use_case.verify_otp_and_activate("inconnu", "123456")
