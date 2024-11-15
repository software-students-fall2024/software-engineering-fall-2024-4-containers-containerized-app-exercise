"""
This module contains unit tests for ml-client.
"""
from unittest.mock import MagicMock, patch
import pytest
#from flask import Flask
from app import app


@pytest.fixture
def test_client():
    """Fixture for the Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@patch("app.sr.Recognizer")
def test_transcribe_no_audio(mock_recognizer, test_client):
    """Test the /transcribe endpoint with no audio file provided."""
    response = test_client.post("/transcribe", content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json == {
        "status": "fail",
        "text": "No audio file provided",
    }
