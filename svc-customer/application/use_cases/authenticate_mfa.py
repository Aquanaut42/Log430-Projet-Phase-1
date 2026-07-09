# authenticate_mfa.py

import hashlib
from domain.models.customer import Customer, CustomerStatus  # ← import manquant
from domain.models.otp import OTP
from domain.exceptions.customer_exceptions import (
    CustomerNotFound, InvalidOTP, CustomerNotActive
)
from application.ports.customer_repository import CustomerRepository

class AuthenticateMFA:
    def __init__(self, repository: CustomerRepository):

        self.repository = repository

    def verify_credentials(self, username: str, password: str) -> str:

        customer = self.repository.find_by_username(username)
        if not customer:
            raise CustomerNotFound("Client introuvable")

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if customer.password_hash != password_hash:
            raise InvalidOTP("Identifiants invalides")

        return customer.id

    def verify_otp_and_activate(self, customer_id: str, otp_code: str) -> Customer:

        customer = self.repository.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFound("Client introuvable")

        otp = OTP(otp_code)
        if not otp.is_valid():
            raise InvalidOTP("Code OTP invalide")

        customer.activate()
        self.repository.update(customer)
        return customer
