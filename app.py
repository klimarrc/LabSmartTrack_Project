from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "labsmarttrack-dev-secret"


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)

    return wrapper


@app.route("/")
@login_required

@app.route("/rooms")
@login_required
def rooms():
    return "<h1>Rooms page</h1>"


@app.route("/cages")
@login_required
def cages():
    return "<h1>Cages page</h1>"


@app.route("/mice")
@login_required
def mice():
    return "<h1>Mice page</h1>"


@app.route("/breeding")
@login_required
def breeding():
    return "<h1>Breeding page</h1>"


@app.route("/ health_reports")
@login_required
def  Health reports():
    return "<h1>Health Reports page</h1>"


@app.route("/admin/users")
@login_required
def admin_users():
    return "<h1>Admin Users page</h1>"


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


if __name__ == "__main__":
    app.run(debug=True)
