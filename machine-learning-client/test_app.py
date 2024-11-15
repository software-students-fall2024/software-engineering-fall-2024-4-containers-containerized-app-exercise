import pytest
from flask import Flask
from unittest.mock import MagicMock, patch
from app import app


@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("app.sr.Recognizer")
def test_transcribe_no_audio(mock_recognizer, client):
    """Test the /transcribe endpoint with no audio file provided."""
    response = client.post("/transcribe", content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "No audio file provided",
    }
