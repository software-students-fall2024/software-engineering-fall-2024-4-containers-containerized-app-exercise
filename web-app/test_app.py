import pytest
from app import create_app, connect_to_mongo, load_environment_variables
from flask import session
from unittest.mock import patch, MagicMock
import os
import tempfile

@pytest.fixture
def client():
    """Flask test client fixture."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client

@patch("app.pymongo.MongoClient")
def test_login_get(mock_mongo, client):
    """Test the login page (GET)."""
    mock_users = mock_mongo.return_value["hellokittyai_db"]["users"]
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello Kitty AI" in response.data  # Check for relevant page content

@patch("app.pymongo.MongoClient")
def test_login_post_new_user(mock_mongo, client):
    """Test login page (POST) with new user creation."""
    mock_users = mock_mongo.return_value["hellokittyai_db"]["users"]
    mock_users.find_one.return_value = None  # Simulate user not existing
    mock_users.insert_one.return_value = MagicMock(inserted_id="12345")

    response = client.post("/", data={"email": "test@example.com"})
    assert response.status_code == 200
    # Check for a string unique to auth.html
    assert b"Authentication Required" in response.data

@patch("app.authUser")
@patch("app.sendCode")
def test_authenticate(mock_send_code, mock_auth_user, client):
    """Test user authentication."""
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
        sess["code"] = "mock-code"

    mock_auth_user.return_value = "mock-token"

    response = client.post("/authenticate", data={"link": "mock-link"})
    assert response.status_code == 302  # Redirect to chat
    assert session.get("token") == "mock-token"

@patch("app.pymongo.MongoClient")
@patch("app.pycai.Client")
def test_chat_with_character(mock_client, mock_mongo, client):
    """Test chat endpoint."""
    with client.session_transaction() as sess:
        sess["email"] = "test@example.com"
        sess["token"] = "mock-token"

    mock_chat = mock_client.return_value
    mock_chat.get_me.return_value = MagicMock(id="mock-id")
    mock_chat.connect.return_value.__enter__.return_value.new_chat.return_value = (MagicMock(chat_id="mock-chat-id"), None)
    mock_chat.send_message.return_value = MagicMock(name="Kitty", text="Hello, how can I help you?")

    mock_users = mock_mongo.return_value["hellokittyai_db"]["users"]

    response = client.post("/chat", json={"message": "Hi Kitty!"})
    assert response.status_code == 200
    assert response.json == {
        "character_name": "Kitty",
        "character_message": "Hello, how can I help you?",
    }
    mock_users.update_one.assert_called_once()


@patch("app.AudioSegment")
@patch("app.secure_filename")
def test_convert_to_wav(mock_secure_filename, mock_audio_segment, client):
    """Test audio conversion endpoint."""
    mock_secure_filename.return_value = "test.wav"
    mock_audio_segment.from_file.return_value.export.return_value = None

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_audio:
        temp_audio.write(b"Fake audio content")  # Simulate audio file content
        temp_audio.seek(0)
        data = {"audio": (temp_audio, "test.mp3")}

        response = client.post("/convert-to-wav", data=data, content_type="multipart/form-data")
        assert response.status_code == 200
        assert response.json["message"] == "Converted to WAV"
        mock_audio_segment.from_file.assert_called_once()

def test_missing_environment_variables():
    """Test app behavior when environment variables are missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SECRET_KEY is missing. Add it to your .env file."):
            load_environment_variables()

    with patch.dict(os.environ, {"SECRET_KEY": "test-secret"}, clear=True):
        with pytest.raises(ValueError, match="MONGO_URI is missing. Add it to your .env file."):
            load_environment_variables()

@patch("app.pymongo.MongoClient")
def test_connect_to_mongo_success(mock_mongo):
    """Test successful MongoDB connection."""
    mock_mongo.return_value.admin.command.return_value = {"ok": 1}
    mongo_client = connect_to_mongo("mock-uri")
    assert mongo_client.admin.command.call_count == 1

@patch("app.pymongo.MongoClient")
def test_connect_to_mongo_failure(mock_mongo):
    """Test failed MongoDB connection."""
    mock_mongo.side_effect = Exception("Connection failed")
    with pytest.raises(RuntimeError, match="MongoDB connection failed."):
        connect_to_mongo("mock-uri")
        
def connect_to_mongo(mongo_uri):
    """Establish a MongoDB connection."""
    try:
        mongo_client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
        mongo_client.admin.command("ping")
        logging.info("Successfully connected to MongoDB!")
        return mongo_client
    except pymongo.errors.PyMongoError as error:
        logging.error("Failed to connect to MongoDB: %s", error)
        raise RuntimeError("MongoDB connection failed.") from error
