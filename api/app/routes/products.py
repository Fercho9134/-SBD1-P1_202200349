from flask import Blueprint, jsonify, request  # Aquí se debe importar `request` de Flask
from app.services.product_service import crear_producto, obtener_productos, actualizar_produco, borrarProducto

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["POST"])
def post_product():
    product = request.json
    response, status_code = crear_producto(product)
    return jsonify(response), status_code

@products_bp.route("/", methods=["GET"])
def get_products():
    response, status_code = obtener_productos()
    return jsonify(response), status_code

@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    response, status_code = obtener_productos(product_id)
    return jsonify(response), status_code

@products_bp.route("/<int:product_id>", methods=["PUT"])
def put_product(product_id):
    product = request.json
    response, status_code = actualizar_produco(product_id, product)
    return jsonify(response), status_code

@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    response, status_code = borrarProducto(product_id)
    return jsonify(response), status_code