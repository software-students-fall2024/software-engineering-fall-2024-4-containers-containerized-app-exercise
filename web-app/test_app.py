"""
Simplified test suite for the Flask application without pymongo.
"""

import pytest
from app import create_app, decode_photo, handle_error


@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "testsecretkey",
    })
    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_home_page(client):
    """Test the home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to PlatifyAI!" in response.data
    assert b"<a href=\"/login\">Log in</a>" in response.data
    assert b"<a href=\"/signup\">Sign up</a>" in response.data



def test_signup_get(client):
    """Test GET request to signup page."""
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


def test_upload_get(client):
    """Test GET request to upload page."""
    response = client.get("/upload")
    assert response.status_code == 200
    assert b"Upload" in response.data


def test_upload_post_no_photo(client):
    """Test POST request to upload without photo data."""
    response = client.post("/upload", data={})
    assert response.status_code == 400
    assert b"No photo data received" in response.data


def test_decode_photo_valid():
    """Test decode_photo with valid data."""
    valid_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"
    decoded = decode_photo(valid_data)
    assert isinstance(decoded, bytes)


def test_decode_photo_invalid():
    """Test decode_photo with invalid data."""
    invalid_data = "invaliddata"
    with pytest.raises(ValueError) as excinfo:
        decode_photo(invalid_data)
    assert "Invalid photo data" in str(excinfo.value)
