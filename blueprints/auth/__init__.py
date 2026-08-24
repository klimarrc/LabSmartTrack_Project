"""Authentication blueprint package."""

from flask import Blueprint


auth_bp = Blueprint("auth", __name__)



from blueprints.auth import login, password_reset, registration