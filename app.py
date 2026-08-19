import os

from flask import Flask, app, redirect, render_template, session, url_for

from blueprints.dashboard import dashboard_bp
from blueprints.room_qr import room_qr_bp
from blueprints.breeding import breeding_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "labsmarttrack-dev-secret")

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
