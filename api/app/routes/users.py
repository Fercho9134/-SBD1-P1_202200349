from flask import Blueprint, jsonify, request  # Aquí se debe importar `request` de Flask
from app.services.user_service import insert_user, login_user, obtener_usuario, actualizar_usuario, eliminar_usuario

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["POST"])
def post_user():
    user = request.json
    response, status_code = insert_user(user) 
    return jsonify(response), status_code

@users_bp.route("/login", methods=["POST"])
def log_user():
    user = request.json
    response, status_code = login_user(user)
    return jsonify(response), status_code

@users_bp.route("/<int:id_usuario>", methods=["GET"])
def get_user(id_usuario):
    response, status_code = obtener_usuario(id_usuario)
    return jsonify(response), status_code

@users_bp.route("/<int:id_usuario>", methods=["PUT"])
def put_user(id_usuario):
    user = request.json
    response, status_code = actualizar_usuario(id_usuario, user)
    return jsonify(response), status_code

@users_bp.route("/<int:id_usuario>", methods=["DELETE"])
def delete_user(id_usuario):
    response, status_code = eliminar_usuario(id_usuario)
    return jsonify(response), status_code