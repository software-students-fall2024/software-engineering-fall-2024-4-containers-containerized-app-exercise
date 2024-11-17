import pytest
from flask import session, url_for
from app import app, users_collection, emotion_data_collection
import bcrypt



# Fixture for the test client
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    with app.test_client() as client:
        yield client


# Test for the home route
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Update based on your index.html content


# Test the login route - GET
def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data  # Check if "Login" appears in the response


# Test the login route - POST
def test_login_post_success(client, monkeypatch):
    # Mock user data in MongoDB
    hashed_password = bcrypt.hashpw(b"test_pass", bcrypt.gensalt())
    # Mocked user with _id field
    test_user = {"_id": "mock_id", "username": "test_user", "password": hashed_password}


    monkeypatch.setattr(users_collection, "find_one", lambda x: test_user)

    response = client.post("/login", data={"username": "test_user", "password": "test_pass"})
    assert response.status_code == 302  # Redirect after login success
    assert response.headers["Location"].endswith("/dashboard")  # Ensure proper redirect
    with client.session_transaction() as session:
        assert session["username"] == "test_user"  # Verify session data


def test_login_post_fail(client, monkeypatch):
    monkeypatch.setattr(users_collection, "find_one", lambda x: None)

    response = client.post("/login", data={"username": "wrong_user", "password": "wrong_pass"})
    assert response.status_code == 302  # Redirect back to login
    assert url_for("login") in response.headers["Location"]  # Check redirection
    with client.session_transaction() as session:
        assert not session.get("user_id")  # Session should not contain user_id


# Test the signup route - GET
def test_signup_get(client):
    response = client.get("/signup")
    assert response.status_code == 200
    assert b"Sign Up" in response.data  # Check content in response


# Test the signup route - POST
def test_signup_post_success(client, monkeypatch):
    monkeypatch.setattr(users_collection, "find_one", lambda x: None)
    monkeypatch.setattr(users_collection, "insert_one", lambda x: None)

    response = client.post("/signup", data={"username": "new_user", "password": "new_pass"})
    assert response.status_code == 302  # Redirect to login page
    assert url_for("login") in response.headers["Location"]  # Redirect to login


def test_signup_post_fail(client, monkeypatch):
    monkeypatch.setattr(users_collection, "find_one", lambda x: {"username": "existing_user"})

    response = client.post("/signup", data={"username": "existing_user", "password": "pass"})
    assert response.status_code == 302  # Redirect back to signup
    assert url_for("signup") in response.headers["Location"]  # Redirect to signup


# Test the dashboard route
def test_dashboard(client, monkeypatch):
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"

    monkeypatch.setattr(emotion_data_collection, "find_one", lambda x, sort: {
        "emotion": "Happy 😊",
        "timestamp": "2024-11-16T12:00:00"
    })

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Happy 😊" in response.get_data(as_text=True)


# Test the capture route
def test_capture(client, monkeypatch):
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"

    monkeypatch.setattr(emotion_data_collection, "insert_one", lambda x: None)
    monkeypatch.setattr("app.detect_emotion", lambda x: "Sad 😢")

    response = client.post("/capture")
    assert response.status_code == 302  # Redirect to dashboard
    assert url_for("dashboard") in response.headers["Location"]  # Redirect to dashboard


# Test logout
def test_logout(client):
    with client.session_transaction() as session:
        session["user_id"] = "mock_user_id"
        session["username"] = "mock_username"

    response = client.get("/logout")
    assert response.status_code == 302  # Redirect to index
    assert url_for("index") in response.headers["Location"]  # Redirect to home
    with client.session_transaction() as session:
        assert "user_id" not in session  # Session should be cleared


