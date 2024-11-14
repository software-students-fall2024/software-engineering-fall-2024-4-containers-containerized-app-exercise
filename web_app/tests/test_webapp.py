"""
This is a test module for web_app.py
"""

import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
from flask import session, url_for
from io import BytesIO
from werkzeug.security import generate_password_hash
from web_app import app, users_collection

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def client():
    """
    Fixture to create a test client for the Flask application
    """
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_home(client):
    """
    Test the home page to ensure it returns a 200 status code and the welcome message
    """
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_signup_get(client):
    """
    Test the signup route (GET) to ensure it returns a 200 status code and contains the sign-up message.
    """
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


@patch("web_app.requests.post")
@patch("web_app.users_collection.insert_one")
def test_signup_post(mock_insert_one, mock_requests_post, client):
    """
    Test the signup route (POST) to ensure it correctly handles user registration.
    """
    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {"encoding": "test_encoding"}

    data = {
        "username": "testuser",
        "password": "testpassword",
        "image": (BytesIO(b"my file contents"), "test.jpg"),
    }
    response = client.post("/signup", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"] == url_for("login")


def test_login_get(client):
    """
    Test the login route (GET) to ensure it returns a 200 status code and contains the login message.
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


@patch("web_app.users_collection.find_one")
def test_login_post(mock_find_one, client):
    """
    Test the login route (POST) to ensure it correctly handles user login.
    """
    mock_find_one.return_value = {
        "username": "testuser",
        "password": generate_password_hash("testpassword"),
    }
    data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/login", data=data)
    assert response.status_code == 302
    assert response.headers["Location"] == url_for("home")


def test_logout(client):
    """
    Test the logout route to ensure it correctly handles user logout.
    """
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == url_for("login")


@patch("web_app.requests.post")
@patch("web_app.users_collection.find_one")
def test_verify_post(mock_find_one, mock_requests_post, client):
    """
    Test the verify route (POST) to ensure it correctly handles face verification.
    """
    mock_find_one.return_value = {"username": "testuser", "encoding": "test_encoding"}
    mock_requests_post.return_value.status_code = 200
    mock_requests_post.return_value.json.return_value = {"result": "match"}

    with client.session_transaction() as sess:
        sess["username"] = "testuser"

    data = {"image": (BytesIO(b"my file contents"), "test.jpg")}
    response = client.post("/verify", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"match" in response.data
