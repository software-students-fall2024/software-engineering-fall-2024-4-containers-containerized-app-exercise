"""
Tests for the web app code.
"""
import pytest
from flask import session, url_for
from app import app, users_collection, emotion_data_collection
import bcrypt


# Fixture for the test client
@pytest.fixture
def client():
    """
    Flask test client for testing the application.
    """
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    with app.test_client() as client:
        yield client


# Test for the home route
def test_index(client):
    """
    Test the index route for proper response and content.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Update based on your index.html content


# Test the login route - GET
def test_login_get(client):
    """
    Test the GET request for the login route.
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


# Test the login route - POST success
def test_login_post_success(client, monkeypatch):
    """
    Test successful POST request to login with valid credentials.
    """
    hashed_password = bcrypt.hashpw(b"test_pass", bcrypt.gensalt())
    test_user = {"_id": "mock_id", "username": "test_user", "password": hashed_password}

    def mock_find_one(query):
        return test_user

    monkeypatch.setattr(users_collection, "find_one", mock_find_one)

    response = client.post("/login", data={"username": "test_user", "password": "test_pass"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as sess:
        assert sess["username"] == "test_user"


# Test the login route - POST failure
def test_login_post_fail(client, monkeypatch):
    """
    Test failed POST request to login with invalid credentials.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: None)

    response = client.post("/login", data={"username": "wrong_user", "password": "wrong_pass"})
    assert response.status_code == 302
    assert url_for("login") in response.headers["Location"]
    with client.session_transaction() as sess:
        assert "user_id" not in sess


# Test the signup route - GET
def test_signup_get(client):
    """
    Test the GET request for the signup route.
    """
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data


# Test the signup route - POST success
def test_signup_post_success(client, monkeypatch):
    """
    Test successful POST request to signup with valid credentials.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: None)
    monkeypatch.setattr(users_collection, "insert_one", lambda data: None)

    response = client.post("/signup", data={"username": "new_user", "password": "new_pass"})
    assert response.status_code == 302
    assert url_for("login") in response.headers["Location"]


# Test the signup route - POST failure
def test_signup_post_fail(client, monkeypatch):
    """
    Test failed POST request to signup with an existing username.
    """
    monkeypatch.setattr(users_collection, "find_one", lambda query: {"username": "existing_user"})

    response = client.post("/signup", data={"username": "existing_user", "password": "pass"})
    assert response.status_code == 302
    assert url_for("signup") in response.headers["Location"]


# Test the dashboard route
def test_dashboard(client, monkeypatch):
    """
    Test the dashboard route with a valid session and data.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "mock_user_id"

    monkeypatch.setattr(emotion_data_collection, "find_one", lambda query, sort=None: {
        "emotion": "Happy 😊",
        "timestamp": "2024-11-16T12:00:00"
    })

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Happy 😊" in response.get_data(as_text=True)


# Test the capture route
# Test the capture route
def test_capture(client, monkeypatch):
    """
    Test the capture route to ensure emotion is captured successfully.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "mock_user_id"

    # Mock the emotion detection function
    def mock_detect_emotion(frame):
        return "Sad 😢"

    monkeypatch.setattr("app.detect_emotion", mock_detect_emotion)

    # Mock database insertion
    monkeypatch.setattr(emotion_data_collection, "insert_one", lambda data: None)
    response = client.post("/capture", json={"image": "dummy_base64_image_data"})

    # Simulate a POST request to the /capture route
    assert response.status_code == 200  # Ensure the request was successful
    response_json = response.get_json()
    assert response_json["emotion"] == "Sad 😢"  # Check if the captured emotion matches the mock

# Test logout
def test_logout(client):
    """
    Test the logout functionality to clear session and redirect to index.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "mock_user_id"
        sess["username"] = "mock_username"

    response = client.get("/logout")
    assert response.status_code == 302
    assert url_for("index") in response.headers["Location"]
    with client.session_transaction() as sess:
        assert "user_id" not in sess