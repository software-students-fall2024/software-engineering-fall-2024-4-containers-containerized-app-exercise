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


@pytest.fixture(name="test_client")
def _test_client():
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
def test_signup_get(_mock_users_collection, test_client):
    """Test the GET request for the signup page."""
    response = test_client.get("/signup")
    assert response.status_code == 200
    assert b"Register with Your Face" in response.data


@patch("web_app.web_app.users_collection")
def test_signup_post_missing_fields(_mock_users_collection, test_client):
    """Test the POST request for the signup page with missing fields."""
    response = test_client.post(
        "/signup",
        data={"username": "", "email": "", "password": "", "image_data": ""},
    )
    assert response.status_code == 200
    assert b"Username, Email, and Password are required." in response.data


@patch("web_app.web_app.users_collection")
def test_signup_post_existing_email(mock_users_collection, test_client):
    """Test the POST request for the signup page with an existing email."""
    # Mock to return an existing user with the email
    mock_users_collection.find_one.return_value = {"email": "test@example.com"}

    response = test_client.post(
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
def test_signup_post_existing_username(mock_users_collection, test_client):
    """Test the POST request for the signup page with an existing username."""
    # Mock to return an existing user with the username
    mock_users_collection.find_one.side_effect = [None, {"username": "testuser"}]

    response = test_client.post(
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
def test_signup_post_valid_data(mock_requests_post, mock_users_collection, test_client):
    """Test the POST request for the signup page with valid data."""
    # Mock users_collection.find_one to return None (no existing user)
    mock_users_collection.find_one.return_value = None
    # Mock the ML service response for encode_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"encoding": [0.1, 0.2, 0.3]}
    mock_requests_post.return_value = mock_response

    response = test_client.post(
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


def test_login_get(test_client):
    """Test the GET request for the login page."""
    response = test_client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_missing_fields(_mock_users_collection, test_client):
    """Test the POST request for the login page with missing fields."""
    # Missing all fields
    response = test_client.post(
        "/login", data={"username": "", "password": "", "image_data": ""}
    )
    assert response.status_code == 200
    assert b"Username, password, and facial recognition are required." in response.data

    # Missing image_data
    response = test_client.post(
        "/login",
        data={"username": "testuser", "password": "password123", "image_data": ""},
    )
    assert response.status_code == 200
    assert b"Username, password, and facial recognition are required." in response.data

    # Missing password
    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "",
            "image_data": generate_image_data(),
        },
    )
    assert response.status_code == 200
    assert b"Username, password, and facial recognition are required." in response.data

    # Missing username
    response = test_client.post(
        "/login",
        data={
            "username": "",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )
    assert response.status_code == 200
    assert b"Username, password, and facial recognition are required." in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_user_not_found(mock_users_collection, test_client):
    """Test login with a username that does not exist."""
    # Mock to return None (user not found)
    mock_users_collection.find_one.return_value = None

    response = test_client.post(
        "/login",
        data={
            "username": "nonexistentuser",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"User not found." in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_invalid_password(mock_users_collection, test_client):
    """Test login with an invalid password."""
    # Mock to return a user with a specific password hash
    hashed_password = generate_password_hash("correctpassword")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
        "encoding": [0.1, 0.2, 0.3],
    }

    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "wrongpassword",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Invalid password." in response.data


@patch("web_app.web_app.users_collection")
def test_login_post_no_facial_data(mock_users_collection, test_client):
    """Test login when user has no facial data stored."""
    # Mock to return a user without 'encoding' field
    hashed_password = generate_password_hash("password123")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
        # No 'encoding' field
    }

    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"No facial data found for this user." in response.data


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_login_post_face_not_recognized(
    mock_requests_post, mock_users_collection, test_client
):
    """Test login when face is not recognized."""
    # Mock to return a user with encoding
    hashed_password = generate_password_hash("password123")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
        "encoding": [0.1, 0.2, 0.3],
    }

    # Mock the ML service response for recognize_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "not_recognized"}
    mock_requests_post.return_value = mock_response

    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Face not recognized." in response.data


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_login_post_face_recognition_error(
    mock_requests_post, mock_users_collection, test_client
):
    """Test login when face recognition service returns an error."""
    # Mock to return a user with encoding
    hashed_password = generate_password_hash("password123")
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
        "encoding": [0.1, 0.2, 0.3],
    }

    # Mock the ML service response for recognize_face with an error
    mock_response = MagicMock()
    mock_response.json.return_value = {"error": "Error during face recognition."}
    mock_requests_post.return_value = mock_response

    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123",
            "image_data": generate_image_data(),
        },
    )

    assert response.status_code == 200
    assert b"Error during face recognition." in response.data


@patch("web_app.web_app.users_collection")
@patch("web_app.web_app.requests.post")
def test_login_post_valid_credentials_and_face(
    mock_requests_post, mock_users_collection, test_client
):
    """Test login with valid credentials and recognized face."""
    # Mock to return a user with encoding
    hashed_password = generate_password_hash("password123")
    user_encoding = [0.1, 0.2, 0.3]
    mock_users_collection.find_one.return_value = {
        "username": "testuser",
        "password": hashed_password,
        "encoding": user_encoding,
    }

    # Mock the ML service response for recognize_face
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "verified"}
    mock_requests_post.return_value = mock_response

    response = test_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123",
            "image_data": generate_image_data(),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome, testuser" in response.data
    with test_client.session_transaction() as sess:
        assert sess["username"] == "testuser"


def test_logout(test_client):
    """Test the POST request for logging out."""
    # Log in a user
    with test_client.session_transaction() as sess:
        sess["username"] = "testuser"

    response = test_client.post("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"Login" in response.data
    with test_client.session_transaction() as sess:
        assert "username" not in sess


def test_home_not_logged_in(test_client):
    """Test the GET request for the home page when not logged in."""
    response = test_client.get("/home", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_home_logged_in(test_client):
    """Test the GET request for the home page when logged in."""
    with test_client.session_transaction() as sess:
        sess["username"] = "testuser"

    response = test_client.get("/home")
    assert response.status_code == 200
    assert b"Welcome, testuser" in response.data
