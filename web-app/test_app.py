"""
Extended test suite for the Flask application without pymongo.
"""

import os
import pytest
from app import create_app, decode_photo, save_photo


@pytest.fixture
def app():  # pylint: disable=redefined-outer-name
    """Create and configure a new app instance for testing."""
    # Mock environment variables
    os.environ["MONGO_URI"] = "mongodb://mockdb:27017/"
    os.environ["MONGO_DBNAME"] = "test"

    app = create_app()  # pylint: disable=redefined-outer-name
    app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "testsecretkey",
        }
    )
    return app


@pytest.fixture
def client(app):  # pylint: disable=redefined-outer-name
    """A test client for the app."""
    return app.test_client()


def test_home_page(client):  # pylint: disable=redefined-outer-name
    """Test the home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to PlatifyAI!" in response.data
    assert b'<a href="/login">Log in</a>' in response.data
    assert b'<a href="/signup">Sign up</a>' in response.data


def test_signup_get(client):  # pylint: disable=redefined-outer-name
    """Test GET request to signup page."""
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


def test_upload_get(client):  # pylint: disable=redefined-outer-name
    """Test GET request to upload page."""
    response = client.get("/upload")
    assert response.status_code == 200
    assert b"Upload" in response.data


def test_upload_post_no_photo(client):  # pylint: disable=redefined-outer-name
    """Test POST request to upload without photo data."""
    response = client.post("/upload", data={})
    assert response.status_code == 400
    assert b"No photo data received" in response.data


def test_decode_photo_valid():  # pylint: disable=redefined-outer-name
    """Test decode_photo with valid data."""
    valid_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA"
    decoded = decode_photo(valid_data)
    assert isinstance(decoded, bytes)


def test_decode_photo_invalid():  # pylint: disable=redefined-outer-name
    """Test decode_photo with invalid data."""
    invalid_data = "invaliddata"
    with pytest.raises(ValueError) as excinfo:
        decode_photo(invalid_data)
    assert "Invalid photo data" in str(excinfo.value)


def test_save_photo():  # pylint: disable=redefined-outer-name
    """Test save_photo function."""
    photo_binary = b"test binary data"
    uploads_dir = os.path.join("static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    filepath, filename = save_photo(photo_binary)
    assert os.path.exists(filepath)
    assert filename.endswith(".png")

    # Cleanup
    os.remove(filepath)


def test_new_entry_no_id(client):  # pylint: disable=redefined-outer-name
    """Test new_entry route with no ID provided."""
    response = client.get("/new_entry")
    assert response.status_code == 400
    assert b"No entry ID provided" in response.data
