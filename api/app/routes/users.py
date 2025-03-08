from flask import Blueprint, jsonify, request  # Aquí se debe importar `request` de Flask
from app.services.user_service import insert_user

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["POST"])
def post_user():
    user = request.json
    response, status_code = insert_user(user) 
    return jsonify(response), status_code

