import os
from io import BytesIO
from functools import wraps
from dotenv import load_dotenv

import qrcode
from flask import Flask, redirect, render_template, request, send_file, session, url_for

# Import Blueprints
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.breeding_view import breeding_bp

from models import db

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