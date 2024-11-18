import os
import json
from unittest.mock import patch, MagicMock
import speech_recognition as sr
from textblob import TextBlob
import logging
from src.main import app, setup_logging
# Mock environment variables
os.environ["MONGO_URI"] = "mongodb://mock:mock@localhost:27017"

# Set up test client
app.testing = True
client = app.test_client()

def test_process_audio_success(mocker):
    """
    Test successful processing of an audio file.
    """
    # Mock dependencies
    mock_transcribe = mocker.patch("app.utils.transcribe_audio", return_value="Test transcription")
    mock_analyze_sentiment = mocker.patch("app.utils.analyze_sentiment", return_value="positive")
    mock_store_data = mocker.patch("app.utils.store_data")

    # Simulate a valid file upload
    mock_file = (b"audio data", "test_audio.wav")
    response = client.post(
        "/process-audio",
        data={"audio": mock_file, "user_id": "1234"},
        content_type="multipart/form-data",
    )

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["transcript"] == "Test transcription"
    assert data["data"]["sentiment"] == "positive"

    # Ensure mocks were called
    mock_transcribe.assert_called_once_with("./processed_uploads/test_audio.wav")
    mock_analyze_sentiment.assert_called_once_with("Test transcription")
    mock_store_data.assert_called_once()


def test_process_audio_missing_file():
    """
    Test processing when no file is provided.
    """
    response = client.post("/process-audio", data={"user_id": "1234"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "No audio file provided"


def test_process_audio_transcription_failure(mocker):
    """
    Test handling of transcription failure.
    """
    mocker.patch("app.utils.transcribe_audio", side_effect=RuntimeError("Transcription failed"))
    mock_file = (b"audio data", "test_audio.wav")

    response = client.post(
        "/process-audio",
        data={"audio": mock_file, "user_id": "1234"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Runtime error"
    assert "Transcription failed" in data["details"]


def test_process_audio_database_failure(mocker):
    """
    Test handling of database insertion failure.
    """
    mocker.patch("app.utils.transcribe_audio", return_value="Test transcription")
    mocker.patch("app.utils.analyze_sentiment", return_value="positive")
    mocker.patch("app.utils.store_data", side_effect=RuntimeError("Database error"))
    mock_file = (b"audio data", "test_audio.wav")

    response = client.post(
        "/process-audio",
        data={"audio": mock_file, "user_id": "1234"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Runtime error"
    assert "Database error" in data["details"]


def test_logging_configuration():
    """
    Test logging configuration setup.
    """
    setup_logging()
    logger = logging.getLogger("app")
    assert logger.level == logging.DEBUG
    assert logger.handlers


def test_process_audio_file_handling_failure(mocker):
    """
    Test file handling failure during audio processing.
    """
    mocker.patch("app.utils.transcribe_audio", return_value="Test transcription")
    mocker.patch("app.utils.analyze_sentiment", return_value="positive")
    mocker.patch("builtins.open", side_effect=IOError("File handling error"))
    mock_file = (b"audio data", "test_audio.wav")

    response = client.post(
        "/process-audio",
        data={"audio": mock_file, "user_id": "1234"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "File handling failed"
    assert "File handling error" in data["details"]
