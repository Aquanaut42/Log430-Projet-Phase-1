# routes.py

import os
import uuid
from flask import Blueprint, request, jsonify
from application.use_cases.register_customer import RegisterCustomer
from application.use_cases.authenticate_mfa import AuthenticateMFA
from infrastructure.repositories.mongo_customer_repository import MongoCustomerRepository
from domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists, CustomerNotFound, InvalidOTP
)

bp = Blueprint("customer", __name__)

def get_repo():
    return MongoCustomerRepository(os.getenv("MONGO_URI"))

# Sessions en memoire (simple pour Phase 1)
sessions = {}

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@bp.route("/v1/customers", methods=["POST"])
def register():
    data = request.get_json()
    try:
        use_case = RegisterCustomer(get_repo())
        customer = use_case.execute(
            username=data["username"],
            password=data["password"],
            nom=data["nom"],
            adresse=data["adresse"]
        )
        return jsonify({
            "id": customer.id,
            "status": customer.status.value,
            "mfa_hint": "Utilisez le code OTP: 123456"
        }), 201

    except CustomerAlreadyExists as e:
        return jsonify({
            "code": "CUSTOMER_ALREADY_EXISTS",
            "message": str(e),
            "status": 409
        }), 409

    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "status": 500
        }), 500

@bp.route("/v1/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        use_case = AuthenticateMFA(get_repo())
        customer_id = use_case.verify_credentials(
            username=data["username"],
            password=data["password"]
        )
        return jsonify({
            "customer_id": customer_id,
            "mfa_required": True,
            "hint": "Utilisez le code OTP: 123456"
        }), 200

    except (CustomerNotFound, InvalidOTP) as e:
        return jsonify({
            "code": "INVALID_CREDENTIALS",
            "message": str(e),
            "status": 401
        }), 401

@bp.route("/v1/auth/mfa", methods=["POST"])
def mfa():
    data = request.get_json()
    try:
        use_case = AuthenticateMFA(get_repo())
        customer = use_case.verify_otp_and_activate(
            customer_id=data["customer_id"],
            otp_code=data["otp_code"]
        )

        token = str(uuid.uuid4())
        sessions[token] = customer.id

        return jsonify({
            "session_token": token,
            "customer_id": customer.id,
            "status": customer.status.value
        }), 200

    except (CustomerNotFound, InvalidOTP) as e:
        return jsonify({
            "code": "INVALID_MFA_CODE",
            "message": str(e),
            "status": 401
        }), 401

@bp.route("/v1/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    try:
        repo = get_repo()
        customer = repo.find_by_id(customer_id)
        if not customer:
            return jsonify({
                "code": "CUSTOMER_NOT_FOUND",
                "message": "Client introuvable",
                "status": 404
            }), 404

        return jsonify({
            "id": customer.id,
            "status": customer.status.value
        }), 200

    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "status": 500
        }), 500
