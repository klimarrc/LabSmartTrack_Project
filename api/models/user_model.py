"""User model for authentication and authorization."""
from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


from database import db


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    __tablename__ = "user"

    user_id = db.Column(
        db.Integer,
        primary_key=True)

    first_name = db.Column(
        db.String(100),
        nullable=False)
    last_name = db.Column(
        db.String(100),
        nullable=False)
    staff_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False,)
    birth_date = db.Column(
        db.Date,
        nullable=False,
    )
    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False)
    password_hash = db.Column(
        db.String(255),
        nullable=False)
    role = db.Column(
        db.String(30),
        nullable=False,
        default="staff")
    approval_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending",
    )
    enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    def get_id(self):
        """Return the unique identifier for the user."""
        return str(self.user_id)

    @property
    def full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self):
        """Return True if the user is active (enabled and approved)."""
        return (
            self.enabled
            and self.approval_status == "approved"
        )

    def registration_id(self):
        """Return a formatted internal registration ID."""

        if self.user_id is None:
            return None

        return f"LR-{self.user_id:06d}"

    def set_password(self, password):
        """Set the user's password by hashing it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(
            self.password_hash,
            password,
        )
