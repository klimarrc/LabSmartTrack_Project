import os
from io import BytesIO
from functools import wraps
from dotenv import load_dotenv

import qrcode
from flask import Flask, redirect, render_template, request, send_file, session, url_for


from models import db
from flask import Blueprint, render_template
from routes.breeding import breeding_bp, main_bp, auth_bp

breeding_bp = Blueprint("breeding", __name__)

@breeding_bp.route("/breeding")
def breeding():
    return render_template("breeding.html")

load_dotenv()  # Load environment variables from .env file


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL","sqlite:///lab_smart_track.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(breeding_bp)

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized LabSmartTrack database.")

if __name__ == "__main__":
    app.run(debug=True)