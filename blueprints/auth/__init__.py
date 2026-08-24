"""Authentication blueprint package."""

from flask import Blueprint


# Create this first.
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


# Import routes only after auth_bp exists.
from . import login  # noqa: E402, F401
from . import password_reset  # noqa: E402, F401
from . import registration  # noqa: E402, F401
