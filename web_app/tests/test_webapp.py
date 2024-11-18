"""
Unit tests for the web_app module.
"""

import base64
import logging
from unittest.mock import patch, MagicMock
import pytest
from werkzeug.security import generate_password_hash

# Suppress the output from the app during tests
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# Import the app instance directly
from web_app.web_app import app


@pytest.fixture
def client():
    """Fixture to configure the app for testing."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def generate_image_data():
    """Helper function to generate fake base64 image data."""
    return "data:image/jpeg;base64," + base64.b64encode(b"test_image_data").decode(
        "utf-8"
    )


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_signup_get(mock_requests_post, mock_users_collection, client):
    """Test the GET request for the signup page."""
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Register with Your Face" in response.data


@patch("web_app.web_app.users_collection")
def test_signup_post_missing_fields(mock_users_collection, client):
    """Test the POST request for the signup page with missing fields."""
    response = client.post(
        "/signup", data={"username": "", "email": "", "password": "", "image_data": ""}
    )
    assert response.status_code == 200
    assert b"Username, Email, and Password are required." in response.data


@patch("web_app.web_app.users_collection")
def test_signup_post_existing_email(mock_users_collection, client):
    """Test the POST request for the signup page with an existing email."""
    # Mock to return an existing user with the email
    mock_users_collection.find_one.return_value = {"email": "test@example.com"}

    response = client.post(
        "/signup",
        data={
            "username": "newuser",
            "email": "test@example.com",  # existing email
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Email is already registered." in response.data


@patch("web_app.web_app.users_collection")
def test_signup_post_existing_username(mock_users_collection, client):
    """Test the POST request for the signup page with an existing username."""
    # Mock to return an existing user with the username
    mock_users_collection.find_one.side_effect = [None, {"username": "testuser"}]

    response = client.post(
        "/signup",
        data={
            "username": "testuser",  # existing username
            "email": "new@example.com",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Username is already taken." in response.data


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_signup_post_valid_data(mock_requests_post, mock_users_collection, client):
    """Test the POST request for the signup page with valid data."""
    # Mock users_collection.find_one to return None (no existing user)
    mock_users_collection.find_one.return_value = None
    # Mock the ML service response for encode_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"encoding": [0.1, 0.2, 0.3]}
    mock_requests_post.return_value = mock_response

    response = client.post(
        "/signup",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "image_data": generate_image_data(),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Login" in response.data
    mock_users_collection.insert_one.assert_called_once()


def test_login_get(client):
    """Test the GET request for the login page."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_missing_fields(mock_users_collection, client):
    """Test the POST request for the login page with missing fields."""
    response = client.post("/login", data={"username": "", "password": ""})
    assert response.status_code == 200
    assert b"Username and Password are required." in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_invalid_credentials(mock_users_collection, client):
    """Test the POST request for the login page with invalid credentials."""
    # Mock to return a user with a different password
    hashed_password = generate_password_hash("password123")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
    }

    response = client.post(
        "/login", data={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_valid_credentials(mock_users_collection, client):
    """Test the POST request for the login page with valid credentials."""
    hashed_password = generate_password_hash("password123")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
    }

    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome, testuser" in response.data
    with client.session_transaction() as sess:
        assert sess["username"] == "testuser"


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_login_post_facial_recognition_success(
    mock_requests_post, mock_users_collection, client
):
    """Test the POST request for the login page with facial recognition success."""
    # Mock users_collection.find to return users
    users = [
        {"username": "user1", "encoding": [0.1, 0.2, 0.3]},
        {"username": "user2", "encoding": [0.4, 0.5, 0.6]},
    ]
    mock_users_collection.find.return_value = users
    # Mock the ML service response for recognize_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "verified", "matched_index": "1"}
    mock_requests_post.return_value = mock_response

    response = client.post(
        "/login",
        data={
            "username": "user2",
            "password": "password123",
            "image_data": generate_image_data(),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome, user2" in response.data
    with client.session_transaction() as sess:
        assert sess["username"] == "user2"


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_login_post_facial_recognition_failure(
    mock_requests_post, mock_users_collection, client
):
    """Test the POST request for the login page with facial recognition failure."""
    # Mock users_collection.find to return users
    users = [
        {"username": "user1", "encoding": [0.1, 0.2, 0.3]},
        {"username": "user2", "encoding": [0.4, 0.5, 0.6]},
    ]
    mock_users_collection.find.return_value = users
    # Mock the ML service response for recognize_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "not_verified"}
    mock_requests_post.return_value = mock_response

    response = client.post(
        "/login",
        data={
            "username": "user2",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Face not recognized" in response.data
    with client.session_transaction() as sess:
        assert "username" not in sess


def test_logout(client):
    """Test the POST request for logging out."""
    # Log in a user
    with client.session_transaction() as sess:
        sess["username"] = "testuser"

    response = client.post("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    with client.session_transaction() as sess:
        assert "username" not in sess


def test_home_not_logged_in(client):
    """Test the GET request for the home page when not logged in."""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_home_logged_in(client):
    """Test the GET request for the home page when logged in."""
    with client.session_transaction() as sess:
        sess["username"] = "testuser"

    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome, testuser" in response.data
