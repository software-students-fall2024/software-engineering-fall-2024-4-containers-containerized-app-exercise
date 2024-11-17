"""
Tests for the web app routes and functionality.
"""
import base64
import pytest
import bcrypt
import numpy as np
import cv2
from app import app, users_collection, emotion_data_collection

# Fixture for Flask test client
@pytest.fixture
def client():
    """
    Flask test client for testing the application.
    """
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    with app.test_client() as test_client:
        yield test_client


def test_index(client):
    """
    Test the index route for proper response and content.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Update based on your index.html content


def test_login_get(client):
    """
    Test the GET request for the login route.
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_post_success(client, monkeypatch):
    """
    Test successful POST request to login with valid credentials.
    """
    hashed_password = bcrypt.hashpw(b"test_pass", bcrypt.gensalt())
    test_user = {"_id": "mock_id", "username": "test_user", "password": hashed_password}

    def mock_find_one(query):
        return test_user

    monkeypatch.setattr(users_collection, "find_one", mock_find_one)

    response = client.post(
        "/login", data={"username": "test_user", "password": "test_pass"}
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as session:
        assert session["username"] == "test_user"


def test_login_post_fail(client, monkeypatch):
    """
    Test failed POST request to login with invalid credentials.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: None)

    response = client.post(
        "/login", data={"username": "wrong_user", "password": "wrong_pass"}
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_signup_get(client):
    """
    Test the GET request for the signup route.
    """
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


def test_signup_post_success(client, monkeypatch):
    """
    Test successful POST request to signup with valid credentials.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: None)
    monkeypatch.setattr(users_collection, "insert_one", lambda data: None)

    response = client.post(
        "/signup", data={"username": "new_user", "password": "new_pass"}
    )
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_signup_post_fail(client, monkeypatch):
    """
    Test failed POST request to signup with an existing username.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: {"username": "existing_user"})

    response = client.post(
        "/signup", data={"username": "existing_user", "password": "pass"}
    )
    assert response.status_code == 302
    assert "/signup" in response.headers["Location"]


def test_dashboard(client, monkeypatch):
    """
    Test the dashboard route with a valid session and data.
    """
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"

    monkeypatch.setattr(
        emotion_data_collection,
        "find_one",
        lambda query, sort=None: {"emotion": "Happy 😊", "timestamp": "2024-11-16T12:00:00"},
    )

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Happy 😊" in response.get_data(as_text=True)


def test_logout(client):
    """
    Test the logout functionality to clear session and redirect to index.
    """
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"
        session["username"] = "mock_username"

    response = client.get("/logout")
    assert response.status_code == 302
    assert "/" in response.headers["Location"]
    with client.session_transaction() as session:
        assert "user_id" not in session

def test_signup_duplicate_user(client, monkeypatch):
    """
    Test the signup route when trying to register an already existing user.
    """
    def mock_find_one(query):
        return {"username": "existing_user"}

    monkeypatch.setattr("app.users_collection.find_one", mock_find_one)
    
    response = client.post("/signup", data={"username": "existing_user", "password": "password123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username already exists" in response.data


def test_login_invalid_password(client, monkeypatch):
    """
    Test the login route with an invalid password.
    """
    hashed_password = bcrypt.hashpw(b"correct_password", bcrypt.gensalt())
    test_user = {"username": "test_user", "password": hashed_password}

    monkeypatch.setattr("app.users_collection.find_one", lambda query: test_user)
    
    response = client.post("/login", data={"username": "test_user", "password": "wrong_password"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_capture_no_image(client):
    """
    Test the capture route with no image in the request.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "mock_user_id"

    response = client.post("/capture", json={})
    assert response.status_code == 400  # Expect 400 for missing image
    assert response.get_json()["error"] == "No image provided."

def test_login_nonexistent_user(client, monkeypatch):
    """
    Test the login route with a nonexistent user.
    """
    monkeypatch.setattr("app.users_collection.find_one", lambda query: None)
    response = client.post("/login", data={"username": "nonexistent", "password": "wrong_pass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_capture_invalid_base64_image(client, monkeypatch):
    """
    Test the capture route with an invalid Base64-encoded image.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "mock_user_id"

    # Mock the ML client request to avoid actual HTTP call
    def mock_post(*args, **kwargs):
        raise ValueError("Invalid Base64 image")
    
    monkeypatch.setattr("requests.post", mock_post)

    # Send invalid Base64 image
    response = client.post(
        "/capture",
        json={"image": "invalid_base64_data"},
    )
    assert response.status_code == 500
    assert "Error processing the image" in response.get_json()["error"]

def test_homepage(client):
    """
    Test the homepage route to ensure it loads correctly.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_dashboard_empty_data(client, monkeypatch):
    """
    Test the dashboard route when the database returns no emotion data for the user.
    """
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"

    # Mock the database query to return no data
    monkeypatch.setattr(
        "app.emotion_data_collection.find_one",
        lambda query, sort=None: None,
    )

    response = client.get("/dashboard")
    assert response.status_code == 200
    response_text = response.get_data(as_text=True)
    # Updated assertion to match the HTML
    assert "No mood data available yet. Use the camera feed to detect your mood!" in response_text


def test_capture_no_user_session(client):
    """
    Test the capture route without a user session.
    """
    response = client.post("/capture", json={"image": "dummy_base64_data"})
    assert response.status_code == 401  # Expect Unauthorized
    assert response.get_json()["error"] == "Please log in to access this feature."

