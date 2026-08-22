"""LabSmartTrack Flask application."""

import os

from flask import Flask
from flask_login import LoginManager

from database import db

# Import every model so SQLAlchemy can register all relationships.
from api.models.user_model import User


from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Load a user by their unique identifier."""

    return db.session.get(User, int(user_id))


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "labsmarttrack-dev-secret",
    )

    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_directory = os.path.join(basedir, "instance")
    os.makedirs(instance_directory, exist_ok=True)

    database_path = os.path.join(
        instance_directory,
        "labsmarttrack.db",
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{database_path}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)