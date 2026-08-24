LabSmartTrack

LabSmartTrack is a Flask web application for managing laboratory mouse colonies,
including facilities, rooms, racks, cages, mice, strains, breeding pairs,
litters, experiments, staff access, and administrative approvals.

The project uses Flask and SQLite on the backend, with HTML, CSS, Jinja, and
JavaScript on the frontend.

Current features

Dashboard totals for rooms, cages, mice, and upcoming weaning

Facility, room, rack, and cage data models

Mouse, strain, breeding-pair, and litter data models

Experiment and protocol data models

Staff registration with server-side validation

Administrator approval or rejection of registrations

Approved-user login and POST logout

Password hashing with Werkzeug

One-hour password-reset links

Email notifications for registrations and account decisions

CSRF protection and login rate limiting

JavaScript form validation, password matching, confirmation dialogs, search,
and double-submission prevention

Technology

Area

Technology

Backend

Python, Flask

Database

SQLite, Flask-SQLAlchemy

Authentication

Flask-Login

Forms/security

Flask-WTF, CSRF protection

Rate limiting

Flask-Limiter

Frontend

HTML, Jinja, CSS, JavaScript

Email

Python smtplib with TLS

Testing

Pytest (recommended)

Project structure

LabSmartTrack/
├── app.py
├── database.py
├── extensions.py
├── requirements.txt
├── .env
├── .gitignore
├── api/
│   ├── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── user_model.py
│       ├── location_model.py
│       ├── mouse_model.py
│       ├── breeding_model.py
│       └── experiment_model.py
├── blueprints/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── admin.py
│   └── auth/
│       ├── __init__.py
│       ├── registration.py
│       ├── login.py
│       └── password_reset.py
├── services/
│   ├── __init__.py
│   └── email_service.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── admin/
│   │   └── registrations.html
│   └── auth/
│       ├── register.html
│       ├── login.html
│       ├── forgot_password.html
│       └── reset_password.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   │   └── lab_logo.png
│   └── js/
│       ├── base.js
│       ├── dashboard.js
│       ├── admin.js
│       ├── auth-registration.js
│       ├── auth-login.js
│       └── auth-password-reset.js
└── instance/
    └── labsmarttrack.db

The instance directory and database file are generated locally and must not be
committed to Git.

Requirements

Python 3.11 or newer

Windows, macOS, or Linux

A modern browser

SMTP account if email notifications are enabled

Installation on Windows

Open PowerShell in the directory where you want the project:

cd C:\Projects\LabSmartTrack

Create a virtual environment:

py -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Example requirements.txt:

Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
Flask-Limiter
python-dotenv
pytest

Environment configuration

Create .env in the project root:

SECRET_KEY=replace-with-a-long-random-secret
APP_BASE_URL=http://127.0.0.1:5000

ADMIN_EMAIL=administrator@example.com
MAIL_HOST=smtp.example.com
MAIL_PORT=465
MAIL_USERNAME=labsmarttrack@example.com
MAIL_PASSWORD=replace-with-an-email-app-password
MAIL_FROM=labsmarttrack@example.com

Generate a secure Flask secret:

python -c "import secrets; print(secrets.token_hex(32))"

Copy the generated value into SECRET_KEY. Never commit .env or share its
contents.

If using python-dotenv, load the file near the beginning of app.py:

from dotenv import load_dotenv

load_dotenv()

Database configuration

database.py must create the SQLAlchemy object only once:

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

Every model imports the same instance:

from database import db

In app.py, configure and initialize SQLite:

basedir = os.path.abspath(os.path.dirname(__file__))
instance_directory = os.path.join(basedir, "instance")
os.makedirs(instance_directory, exist_ok=True)

database_path = os.path.join(instance_directory, "labsmarttrack.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

Import every model before creating tables so SQLAlchemy can resolve all
relationships:

import api.models

with app.app_context():
    db.create_all()

db.create_all() creates missing tables but does not modify existing columns.
Use Flask-Migrate when the schema begins changing regularly.

Extension initialization

extensions.py contains shared security extensions:

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

Initialize them inside create_app():

from extensions import csrf, limiter

csrf.init_app(app)
limiter.init_app(app)

Use shared Redis-backed rate-limit storage in production instead of
memory://.

Register blueprints

from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)

Run the application

python app.py

Open:

http://127.0.0.1:5000

Common routes:

Route

Purpose

/

Dashboard

/register

Staff access request

/login

Approved-user login

/forgot-password

Request a password-reset link

/admin/registrations

Admin review of pending staff

Staff registration and approval workflow

A staff member submits the registration form.

The account is stored with approval_status="pending".

The administrator receives a notification email.

The administrator logs in and opens /admin/registrations.

The administrator approves or rejects the request.

The staff member receives a decision email.

Only an approved and enabled account can log in.

Registration may request only these roles:

staff
researcher
supervisor

Public registration must never allow a user to request or assign the admin
role.

Create the first administrator

The first administrator must be created manually because no existing admin is
available to approve the account.

Open the Flask shell:

flask --app app shell

Create the account:

from datetime import date

from api.models.user_model import User
from database import db

admin = User(
    email="admin@labsmarttrack.com",
    first_name="System",
    last_name="Administrator",
    staff_id="ADMIN-001",
    birth_date=date(1990, 1, 1),
    requested_role="staff",
    role="admin",
    approval_status="approved",
    enabled=True,
)

admin.set_password("ReplaceWithAStrongPassword123!")

db.session.add(admin)
db.session.commit()

Exit:

exit()

Replace the example identity and password with authorized administrator details.

Authentication behavior

Passwords are hashed and never stored as readable text.

Pending users cannot log in.

Rejected or disabled users cannot log in.

Login responses do not reveal whether an unknown email exists.

Password-reset requests return the same response for known and unknown emails.

Password-reset links expire after one hour.

Reset links become invalid after the password changes.

Logout uses a CSRF-protected POST form.

CSRF protection

Every POST form must contain:

<input
    type="hidden"
    name="csrf_token"
    value="{{ csrf_token() }}"
>

This includes registration, login, logout, approval, rejection, password-reset,
and data-management forms.

JavaScript

JavaScript provides progressive interface improvements:

Registration validation and password matching

Show/hide password controls

Submit-button disabling to prevent double submissions

Administrator approval and rejection confirmation

Pending-registration search

Dashboard count animation

Flash-message dismissal and navigation highlighting

JavaScript must never be the only validation or authorization layer. Flask must
validate every value and permission again on the server.

The end of base.html must expose a script block:

<script
    src="{{ url_for('static', filename='js/base.js') }}"
    defer
></script>

{% block scripts %}{% endblock %}

Email notifications

Email messages are sent through the configured SMTP server using TLS. The
application can notify:

Admin when a new registration is submitted

Staff when registration is approved

Staff when registration is rejected

Staff when a password reset is requested

Approval and rejection must occur inside the protected application. Email
should link the administrator to the review page, not perform a database change
with a GET request.

If email delivery fails after a decision, the database decision remains saved
and the failure is recorded in the application log.

Security requirements

Never deploy with debug=True.

Never commit .env, SQLite files, passwords, tokens, or secret keys.

Use HTTPS and secure cookies in production.

Protect all modifying requests with CSRF.

Apply rate limits to login, registration, and password-reset routes.

Keep administrator authorization checks on the server.

Use SQLAlchemy parameters instead of constructing raw SQL from input.

Do not use Jinja's |safe filter with user-provided text.

Validate and quote every user-controlled HTML attribute.

Restrict access to sensitive information such as staff IDs and birth dates.

Collect birth dates only when the facility has a legitimate requirement.

Back up the database securely and test restoration procedures.

Development database warning

Deleting this file removes all local data:

instance/labsmarttrack.db

Only recreate the database when it contains disposable development data. Use
database migrations for important or production data.

Inspect SQLite

Open the database with DB Browser for SQLite:

instance/labsmarttrack.db

Do not open or edit the .db file in an ordinary text editor.

Git

Recommended .gitignore:

.venv/
venv/
.env
instance/
*.db
__pycache__/
*.py[cod]
.pytest_cache/