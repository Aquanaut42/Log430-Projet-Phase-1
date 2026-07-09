# routes.py

import os
import uuid
from flask import Blueprint, request, jsonify
from application.use_cases.place_order import PlaceOrder
from application.use_cases.activate_line import ActivateLine
from application.use_cases.get_usage import GetUsage
from infrastructure.repositories.mongo_order_repository import MongoOrderRepository
from domain.exceptions.order_exceptions import (
    OrderAlreadyExists, CustomerNotActive,
    LineAlreadyExists, LineNotFound
)

bp = Blueprint("order", __name__)

def get_repo():
    return MongoOrderRepository(os.getenv("MONGO_URI"))

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@bp.route("/v1/orders", methods=["POST"])
def place_order():
    data = request.get_json()
    idempotency_key = request.headers.get(
        "Idempotency-Key", str(uuid.uuid4())
    )
    try:
        use_case = PlaceOrder(get_repo())
        order = use_case.execute(
            customer_id=data["customer_id"],
            plan_id=data["plan_id"],
            idempotency_key=idempotency_key
        )
        return jsonify({
            "id": order.id,
            "customer_id": order.customer_id,
            "status": order.status.value,
            "items": [
                {
                    "plan_id": item.plan_id,
                    "plan_name": item.plan_name,
                    "price": item.price
                }
                for item in order.items
            ]
        }), 201

    except CustomerNotActive as e:
        return jsonify({
            "code": "CUSTOMER_NOT_ACTIVE",
            "message": str(e),
            "status": 403
        }), 403

    except ValueError as e:
        return jsonify({
            "code": "PLAN_NOT_FOUND",
            "message": str(e),
            "status": 404
        }), 404

    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "status": 500
        }), 500

@bp.route("/v1/lines/activate", methods=["POST"])
def activate_line():
    data = request.get_json()
    try:
        use_case = ActivateLine(get_repo())
        line = use_case.execute(
            customer_id=data["customer_id"],
            plan_id=data["plan_id"]
        )
        return jsonify({
            "id": line.id,
            "customer_id": line.customer_id,
            "msisdn": line.msisdn,
            "plan_id": line.plan_id,
            "status": line.status.value
        }), 201

    except LineAlreadyExists as e:
        return jsonify({
            "code": "LINE_ALREADY_EXISTS",
            "message": str(e),
            "status": 409
        }), 409

    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "status": 500
        }), 500

@bp.route("/v1/usage/<customer_id>", methods=["GET"])
def get_usage(customer_id):
    try:
        use_case = GetUsage(get_repo())
        result = use_case.execute(customer_id)
        return jsonify(result), 200

    except LineNotFound as e:
        return jsonify({
            "code": "LINE_NOT_FOUND",
            "message": str(e),
            "status": 404
        }), 404

    except Exception as e:
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "status": 500
        }), 500
