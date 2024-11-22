"""
Unit tests for Flask app for Hello Kitty AI application
"""
import os
import pytest
from flask import session
from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    """Set up the Flask test client."""
    os.environ["SECRET_KEY"] = "d0a1bcfbbd90ac46f4b873a51b6eb2b5873e2a03438b44adf9bbf6bde14de788"
    os.environ["MONGO_URI"] = "mongodb+srv://vernairesl:Iloveu325@cluster0.jy4go.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/vernairesl/SE/4-containers-ghost-in-the-machine/web-app/service_account.json"

    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_session_data():
    """Mock session data for testing."""
    return {
        "email": "test_user@example.com",
        "code": "12345",
        "token": "mock_token",
    }


def test_login_get(client):
    """Test the GET request to the login route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>Login</title>" in response.data


def test_login_post(client):
    """Test the POST request to the login route."""
    response = client.post("/", data={"email": "test_user@example.com"})
    assert response.status_code == 200
    assert b"test_user@example.com" in response.data


def test_login_post_no_email(client):
    """Test the POST request to the login route with missing email."""
    response = client.post("/", data={})
    assert response.status_code == 400
    assert b"Email address is required" in response.data


def test_authenticate_missing_link(client, mock_session_data):
    """Test the authenticate route with a missing link."""
    with client.session_transaction() as session:
        session.update(mock_session_data)

    response = client.post("/authenticate", data={"link": ""})
    assert response.status_code == 400
    assert b"Authentication link is required" in response.data


def test_authenticate_expired_session(client):
    """Test the authenticate route with an expired session."""
    response = client.post("/authenticate", data={"link": "mock_link"})
    assert response.status_code == 403
    assert b"Session expired. Please log in again." in response.data


def test_home_unauthenticated(client):
    """Test the home route for an unauthenticated user."""
    response = client.get("/home")
    assert response.status_code == 403
    assert b"Client is not authenticated. Please log in." in response.data


def test_home_authenticated(client, mock_session_data):
    """Test the home route for an authenticated user."""
    with client.session_transaction() as session:
        session.update(mock_session_data)

    response = client.get("/home")
    assert response.status_code == 200
    assert b"<img src=" in response.data


def test_chat_with_character_get(client):
    """Test the GET request to the chat_with_character route."""
    response = client.get("/chat")
    assert response.status_code == 200
    assert b"Chat with Your Boyfriend" in response.data


def test_chat_with_character_post_unauthenticated(client):
    """Test the POST request to the chat_with_character route for unauthenticated user."""
    response = client.post("/chat", json={"message": "Hello!"})
    assert response.status_code == 403
    assert b"Client is not authenticated. Please log in." in response.data


@patch("app.pycai.Client", autospec=True)
def test_chat_with_character_post_authenticated(mock_client_class, client, mock_session_data):
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        pytest.skip("Google credentials not set. Skipping test.")
    
    with client.session_transaction() as session:
        session.update(mock_session_data)

    mock_client = mock_client_class.return_value
    mock_client.get_me.return_value = MagicMock(id="mock_user_id")
    mock_chat = MagicMock()

    mock_client.connect.return_value.__enter__.return_value = mock_chat
    mock_client.connect.return_value.__exit__.return_value = None 

    mock_chat.new_chat.return_value = (MagicMock(chat_id="mock_chat_id"), MagicMock())
    mock_chat.send_message.return_value = MagicMock(name="MockCharacter", text="Hello!")

    print("Mock Client:", mock_client)
    print("Mock Chat Object:", mock_chat)

    response = client.post("/chat", json={"message": "Hello!"})

    assert response.status_code == 200
    assert b"MockCharacter" in response.data
    assert b"Hello!" in response.data
