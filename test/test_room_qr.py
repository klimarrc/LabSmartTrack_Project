import sys
import os
# This forces Python to look in the main LabSmartTrack folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from room import room_qr_bp

import pytest
from flask import Flask
from unittest.mock import patch


from data.room_qr_data import ROOMS
from app.services.room_service import room_summary, get_room


@pytest.fixture
def app():
    """Creates a dummy Flask application for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"  # Required for flash messages
    
    # Register the blueprint
    app.register_blueprint(room_qr_bp)
    
    return app

@pytest.fixture
def client(app):
    """Provides a test client to simulate web requests."""
    return app.test_client()

### --- Test Cases --- ###

def test_rooms_list(client):
    """Test that the main rooms list loads successfully."""
    response = client.get("/rooms")
    
    assert response.status_code == 200
    # Ensure a known room name is in the rendered HTML
    assert b"Mouse Room A" in response.data

def test_room_scan_valid(client):
    """Test that a valid room ID loads the room dashboard."""
    response = client.get("/rooms/RM-A")
    
    assert response.status_code == 200
    assert b"Winnipeg" in response.data

def test_room_scan_invalid(client):
    """Test that an invalid room ID returns a 404 error."""
    response = client.get("/rooms/INVALID-ID")
    
    assert response.status_code == 404
    assert b"Room not found" in response.data

def test_room_qr_code(client):
    """Test that the QR code endpoint generates a PNG image."""
    response = client.get("/rooms/RM-A/qr.png")
    
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    # Ensure the response actually contains binary data
    assert len(response.data) > 0 

# Patch the NotificationService exactly where it is imported in room_qr.py
@patch("room_qr.NotificationService")
def test_submit_room_check(mock_notification_service_class, client):
    """Test that submitting a room check triggers the notification service."""
    # Get the mock instance that replaces the real NotificationService()
    mock_notifier_instance = mock_notification_service_class.return_value
    
    # Simulate a POST request with form data
    form_data = {
        "staff_name": "Jane Doe",
        "note": "Water bottles refilled."
    }
    response = client.post("/rooms/RM-A/check", data=form_data)
    
    # Assert it redirects back to the room scan page (Status 302)
    assert response.status_code == 302
    assert "/rooms/RM-A" in response.headers["Location"]
    
    # Assert the notification service was called exactly once
    mock_notifier_instance.send_room_check.assert_called_once()
    
    # Verify it was called with the correct form data
    called_args = mock_notifier_instance.send_room_check.call_args.kwargs
    assert called_args["staff_name"] == "Jane Doe"
    assert called_args["note"] == "Water bottles refilled."