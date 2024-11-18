import pytest
from app import app  # Import your Flask app
from flask import Flask
from flask_login import login_user, LoginManager
from unittest.mock import MagicMock
from bson.objectid import ObjectId

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_user():
    # Mock user for login
    user = MagicMock()
    user.id = "some-user-id"
    user.username = "test_user"
    return user

def test_register(client):
    response = client.post("/register", data={"username": "new_user", "password": "password", "repassword": "password"})
    assert response.status_code == 302  # Should redirect to login page

def test_login(client, mock_user):
    # Simulate a logged-in user
    login_user(mock_user)
    response = client.get("/login")
    assert response.status_code == 200  # Login page should render

def test_upload_audio(client, mock_user):
    # Mock file upload and ML client call
    data = {"audio": (io.BytesIO(b"fake audio data"), "fake_audio.wav")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200  # Assuming the ML client response is OK

def test_mood_trends(client, mock_user):
    # Assuming user is logged in
    login_user(mock_user)
    response = client.get("/api/mood-trends")
    assert response.status_code == 200
    assert "Positive" in response.json
    assert "Negative" in response.json

def test_recent_entries(client, mock_user):
    login_user(mock_user)
    response = client.get("/api/recent-entries")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_delete_entry(client, mock_user):
    # Mock deletion of a journal entry by ID
    entry_id = ObjectId()
    response = client.delete(f"/delete-journal/{entry_id}")
    assert response.status_code == 200
    assert "Entry deleted successfully" in response.json["message"]
