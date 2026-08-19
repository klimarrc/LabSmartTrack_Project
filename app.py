import os
from flask import Flask, redirect, render_template, session, url_for

# 1. Import your database instance
from database import db

# 2. Import your models so SQLAlchemy knows what tables to create!
from api.models.physical_model import Location, Facility, Room, Rack, Cage
from api.models.colony_model import Strain, BreedingPair, Litter
from api.models.experiment_model import Protocol, Experiment
from api.models.mouse_model import Mouse

from blueprints.dashboard import dashboard_bp
from blueprints.room_qr import room_qr_bp
from blueprints.breeding import breeding_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "labsmarttrack-dev-secret")

    # --- DATABASE SETUP ---
    # Create the database file inside your 'instance' folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'labsmarttrack.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Connect the database to this Flask app
    db.init_app(app)

    # Create the tables! (This runs once when the app starts)
    with app.app_context():
        db.create_all()
        print("✅ Database successfully connected and tables verified!")
    # ----------------------

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(breeding_bp)
    app.register_blueprint(room_qr_bp)

    @app.context_processor
    def inject_current_user():
        return {"current_user": session.get("user")}

    @app.route("/login")
    def login():
        session["user"] = {"name": "Demo Staff", "role": "staff"}
        return redirect(url_for("dashboard.dashboard"))

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("dashboard.dashboard"))

    @app.route("/roomQr")
    def room_qr():
        return render_template("page.html", title="Room QR Codes", eyebrow="Colony Management")
    
    @app.route("/cages")
    def cages():
        return render_template("page.html", title="Cages", eyebrow="Colony Management")

    @app.route("/mice")
    def mice():
        return render_template("page.html", title="Mice", eyebrow="Colony Management")

    @app.route("/breeding")
    def breeding():
        return render_template("page.html", title="Breeding", eyebrow="Breeding")

    @app.route("/reports")
    def reports():
        return render_template("page.html", title="Reports", eyebrow="Analysis")

    @app.route("/admin/users")
    def admin_users():
        return render_template("page.html", title="Admin Users", eyebrow="Administration")
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)