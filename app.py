"""LabSmartTrack Flask application."""
import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from api.models.user_model import User
from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from database import db
from extensions import csrf, limiter

import api.models.breeding_model as _breeding_models
import api.models.experiment_model as _experiment_models
import api.models.location_model as _location_models
import api.models.mouse_model as _mouse_models

load_dotenv()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Load the authenticated user from the database."""
    try:
        parsed_user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(User, parsed_user_id)


def create_app(test_config=None):
    """Create and configure the LabSmartTrack application."""

    basedir = os.path.abspath(
        os.path.dirname(__file__)
    )

    template_directory = os.path.join(
        basedir,
        "templates",
    )

    static_directory = os.path.join(
        basedir,
        "static",
    )

    instance_directory = os.path.join(
        basedir,
        "instance",
    )

    os.makedirs(
        instance_directory,
        exist_ok=True,
    )

    database_path = os.path.join(
        instance_directory,
        "labsmarttrack.db",
    )

    app = Flask(
        __name__,
        template_folder=template_directory,
        static_folder=static_directory,
    )

    production = (
        os.getenv("FLASK_ENV", "development").lower()
        == "production"
    )

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=(
            f"sqlite:///{database_path}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,

        APP_BASE_URL=os.getenv(
            "APP_BASE_URL",
            "http://127.0.0.1:5000",
        ),

        ADMIN_EMAIL=os.getenv("ADMIN_EMAIL"),

        MAIL_HOST=os.getenv("MAIL_HOST"),
        MAIL_PORT=int(
            os.getenv("MAIL_PORT", "465")
        ),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),

        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=production,

        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_SECURE=production,

        PERMANENT_SESSION_LIFETIME=timedelta(
            minutes=30
        ),

        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        MAX_FORM_MEMORY_SIZE=100 * 1024,
        MAX_FORM_PARTS=100,
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Pytest can replace the database and security settings.
    secret_key = app.config.get("SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "The SECRET_KEY environment variable is required."
        )

    if not app.config["TESTING"] and len(secret_key) < 32:
        raise RuntimeError(
            "SECRET_KEY must contain at least 32 characters."
        )

    # Connect Flask extensions.
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.login_message_category = None

    # Register each blueprint once.
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    add_security_headers(app)

    return app


def add_security_headers(app):
    """Add browser security headers to every response."""

    @app.after_request
    def apply_headers(response):
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'"
        )

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        return response


if __name__ == "__main__":
    application = create_app()

    application.run(
        debug=os.getenv("FLASK_DEBUG") == "1"
    )
