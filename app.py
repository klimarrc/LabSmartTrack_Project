from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for

from models import db


app = Flask(__name__)
app.config["SECRET_KEY"] = "labsmarttrack-dev-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///labsmarttrack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)

    return wrapper


@app.route("/")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        room_count=0,
        cage_count=0,
        mouse_count=0,
        weaning_due=0,
    )


@app.route("/rooms")
@login_required
def rooms():
    return render_template("rooms.html")


@app.route("/rooms/<int:room_id>/check")
@login_required
def room_check(room_id):
    return render_template("room_check.html", room_id=room_id)


@app.route("/cages")
@login_required
def cages():
    return render_template("cages.html")


@app.route("/cages/<int:cage_id>")
@login_required
def cage_detail(cage_id):
    return render_template("cage_detail.html", cage_id=cage_id)


@app.route("/mice")
@login_required
def mice():
    return render_template("mice.html")


@app.route("/breeding")
@login_required
def breeding():
    return render_template("breeding.html")


@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


@app.route("/admin/users")
@login_required
def admin_users():
    return render_template("admin_users.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session["user"] = {"username": username, "role": "admin"}
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Initialized LabSmartTrack database.")


if __name__ == "__main__":
    app.run(debug=True)
