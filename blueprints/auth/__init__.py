"""Authentication blueprint package."""
from flask import Blueprint

## Import the login, password_reset, and registration blueprints
from blueprints.auth import login, password_reset, registration
from blueprints.auth import auth_bp

auth_bp = Blueprint("auth", __name__)

auth_bp.register_blueprint(login)
auth_bp.register_blueprint(password_reset)
auth_bp.register_blueprint(registration)