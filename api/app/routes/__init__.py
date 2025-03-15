from flask import Blueprint
from .users import users_bp
from .products import products_bp
from .ordenes import ordenes_bp

# Crear un blueprint global con el prefijo "/api"
api_bp = Blueprint("api", __name__, url_prefix="/api")

def register_routes(app):
    blueprints = [
        (users_bp, "/users"),
        (products_bp, "/products"),
        (ordenes_bp, "/orders")
    ]
    for bp, prefix in blueprints:
        api_bp.register_blueprint(bp, url_prefix=prefix)


    app.register_blueprint(api_bp)
