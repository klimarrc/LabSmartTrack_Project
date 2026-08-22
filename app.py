import os

from flask import Flask, redirect, render_template, session, url_for

from database import db

# Import models so SQLAlchemy can discover their tables.
from api.models.location_model import Location, Facility, Room, Rack, Cage
from api.models.breeding_model import Strain, BreedingPair, Litter
from api.models.experiment_model import Protocol, Experiment
from api.models.mouse_model import Mouse

from blueprints.dashboard import dashboard_bp
from blueprints.room_qr import room_qr_bp
from blueprints.breeding import breeding_bp


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "labsmarttrack-dev-secret"
    )

    # Create the instance directory if it does not exist.
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_directory = os.path.join(basedir, "instance")
    os.makedirs(instance_directory, exist_ok=True)

    database_path = os.path.join(
        instance_directory,
        "labsmarttrack.db"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{database_path}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Create tables that do not already exist.
    with app.app_context():
        db.create_all()
        print("Database connected and tables verified.")

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(breeding_bp)
    app.register_blueprint(room_qr_bp)

    @app.context_processor
    def inject_current_user():
        return {"current_user": session.get("user")}

    @app.route("/login")
    def login():
        session["user"] = {
            "name": "Demo Staff",
            "role": "staff"
        }
        return redirect(url_for("dashboard.dashboard"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("dashboard.dashboard"))

    @app.route("/cages")
    def cages():
        return render_template(
            "page.html",
            title="Cages",
            eyebrow="Colony Management"
        )

    @app.route("/mice")
    def mice():
        return render_template(
            "page.html",
            title="Mice",
            eyebrow="Colony Management"
        )

    @app.route("/reports")
    def reports():
        return render_template(
            "page.html",
            title="Reports",
            eyebrow="Analysis"
        )

    @app.route("/admin/users")
    def admin_users():
        return render_template(
            "page.html",
            title="Admin Users",
            eyebrow="Administration"
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)