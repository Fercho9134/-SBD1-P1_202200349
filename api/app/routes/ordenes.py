from flask import Blueprint, jsonify, request
from app.services.ordenes_service import insert_order, get_all_orders, get_order_by_id

ordenes_bp = Blueprint("orders", __name__)

@ordenes_bp.route("/", methods=["POST"])
def post_order():
    data = request.json
    response, status_code = insert_order(data)
    return jsonify(response), status_code


@ordenes_bp.route("/", methods=["GET"])
def get_orders():
    response, status_code = get_all_orders()
    return jsonify(response), status_code

@ordenes_bp.route("/<int:id>", methods=["GET"])
def get_order(id):
    response, status_code = get_order_by_id(id)
    return jsonify(response), status_code

