"""
This is the tests for the webapp
"""

from io import BytesIO

# pylint: disable=unused-import
from unittest.mock import patch

# pylint: disable=unused-import
import pytest

# pylint: disable=unused-import
# pylint: disable=import-error
from src.app import app, audio_collection, metadata_collection


def test_record_route(test_client):
    """Test that the record route '/' works."""
    response = test_client.get("/record")
    assert response.status_code == 200


@patch("src.app.audio_collection.insert_one")
def test_missing_filename(mock_audio, test_client):
    """Test missing filename"""
    file_info = (BytesIO(b"fake_audio_data"), "test_audio.wav")
    response = test_client.post("/upload-audio", data={"audio": file_info})
    assert response.status_code == 400
    assert not mock_audio.called


@patch("src.app.audio_collection.insert_one")
@patch("src.app.requests.get")
@patch("src.app.metadata_collection.insert_one")
def test_upload_audio(mock_req, mock_md, mock_audio, test_client):
    """Test uploading audio"""
    mock_audio.return_value.inserted_id = "mock_file"
    mock_md.return_value.acknowledged = True
    mock_req.return_value.ok = True
    mock_req.return_value.text = "Success"

    data = {
        "name": "test_audio",
    }
    file_info = (BytesIO(b"fake_audio_data"), "test_audio.wav")
    response = test_client.post("/upload-audio", data={"audio": file_info, **data})

    assert response.status_code == 302
    assert mock_audio.called
    assert mock_md.called
    assert mock_req.called


@patch("src.app.audio_collection.insert_one")
@patch("src.app.metadata_collection.insert_one")
def test_db_failure(mock_md, mock_audio, test_client):
    """Test failure when database insertion fails"""
    mock_audio.return_value.inserted_id = None  # Simulating the failure
    mock_md.return_value.acknowledged = False  # Simulating failure in metadata insert

    data = {
        "name": "test_audio",
    }
    file_info = (BytesIO(b"fake_audio_data"), "test_audio.wav")

    response = test_client.post("/upload-audio", data={"audio": file_info, **data})

    assert response.status_code == 500


@patch("src.app.audio_collection.insert_one")
def test_audio_missing(mock_audio, test_client):
    """test without audio"""
    response = test_client.post("/upload-audio", data={"name": "test_audio"})
    assert response.status_code == 400
    assert not mock_audio.called
