from flask import Blueprint, jsonify, request  # Aquí se debe importar `request` de Flask
from app.services.product_service import crear_producto

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["POST"])
def post_product():
    product = request.json
    response, status_code = crear_producto(product)
    return jsonify(response), status_code