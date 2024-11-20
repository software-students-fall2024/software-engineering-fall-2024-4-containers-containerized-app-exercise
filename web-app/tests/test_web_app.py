"""
This is the tests for the webapp
"""

from datetime import datetime
import pytest
from flask import Flask
from pymongo.collection import Collection
from gridfs import GridFS
from io import BytesIO

# pylint: disable=unused-import
# pylint: disable=import-error
from src.app import app, metadata_collection, grid_fs


def test_record_route(test_client):
    """Test that the record route works"""
    response = test_client.get("/record")
    assert response.status_code == 200


def test_upload_audio_missing(test_client):
    """
    Test that the /upload-audio route handles missing fields properly
    """
    response = test_client.post("/upload-audio", data={})
    assert response.status_code == 400
    assert response.json == {"error": "Audio file and name are required"}


def test_upload_audio_gridfs_fail(test_client, monkeypatch):
    """
    Test failure in Gridfs
    """

    def mock_put(*args, **kwargs):
        return None

    monkeypatch.setattr(grid_fs, "put", mock_put)

    file_data = (BytesIO(b"audio"), "audio.wav")

    response = test_client.post(
        "/upload-audio",
        data={"audio": file_data, "name": "audio"},
    )

    assert response.status_code == 500

    assert response.json == {"error": "Failed to store the audio file in GridFS"}


def test_upload_audio_metadata(test_client, monkeypatch):
    """
    Test failure during storing metadata
    """

    def mock_insert(metadata):
        class Result:
            acknowledged = False

        return Result()

    monkeypatch.setattr(metadata_collection, "insert_one", mock_insert)

    def mock_put(*args, **kwargs):
        return "mock_gridfs"

    monkeypatch.setattr(grid_fs, "put", mock_put)

    file = (BytesIO(b"audio"), "audio.wav")
    response = test_client.post(
        "/upload-audio",
        data={"audio": file, "name": "audio"},
    )

    assert response.status_code == 500
    assert response.json == {"error": "Failed to store the metadata in the database"}


def test_upload_audio_ml(test_client, monkeypatch):
    """
    Test failure to notify ML client
    """

    def mock_insert(metadata):
        class Result:
            acknowledged = True

        return Result()

    def mock_put(*args, **kwargs):
        return "mock_gridfs"

    def mock_get(*args, **kwargs):
        class Response:
            status_code = 500
            text = "ML client error"

        return Response()

    monkeypatch.setattr(metadata_collection, "insert_one", mock_insert)
    monkeypatch.setattr(grid_fs, "put", mock_put)
    monkeypatch.setattr("src.app.requests.get", mock_get)

    file = (BytesIO(b"audio"), "audio.wav")
    response = test_client.post(
        "/upload-audio",
        data={"audio": file, "name": "audio"},
    )

    assert response.status_code == 500
    assert (
        response.json["message"]
        == "File uploaded, but ML client responded with an error."
    )
    assert response.json["ml_client_response"] == "ML client error"


def test_upload_audio(test_client, monkeypatch):
    """
    Test successful upload
    """

    def mock_insert(metadata):
        class Result:
            acknowledged = True

        return Result()

    def mock_put(*args, **kwargs):
        return "mock_gridfs"

    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = "Success"

        return MockResponse()

    monkeypatch.setattr(metadata_collection, "insert_one", mock_insert)
    monkeypatch.setattr(grid_fs, "put", mock_put)
    monkeypatch.setattr("src.app.requests.get", mock_get)

    file = (BytesIO(b"audio"), "audio.wav")

    response = test_client.post(
        "/upload-audio",
        data={"audio": file, "name": "audio"},
    )

    assert response.status_code == 200

    assert (
        response.json["message"]
        == "File uploaded successfully, and ML client notified."
    )

    assert response.json["file_id"] == "mock_gridfs"
