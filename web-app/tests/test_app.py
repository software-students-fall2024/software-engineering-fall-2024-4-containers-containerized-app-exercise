"""
This module contains unit tests for the application.
"""

import io
from pathlib import Path
import pytest


from app import create_app  # pylint: disable=import-error


@pytest.fixture
def client():  # pylint: disable=redefined-outer-name
    """Fixture for the Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


def test_root1(client):  # pylint: disable=redefined-outer-name
    """Test the / route on GET req"""
    response = client.get("/")
    html_text = response.data.decode("utf-8")
    assert "Start Recording" in html_text
    assert response.status_code == 200


def test_root2(client):  # pylint: disable=redefined-outer-name
    """Test the / route on GET req"""
    response = client.get("/")
    html_text = response.data.decode("utf-8")
    assert "Waiting for permission to access the microphone..." in html_text
    assert response.status_code == 200


def test_404(client):  # pylint: disable=redefined-outer-name
    """Test a non-existent route, expecting 404 error"""
    response = client.get("/non-existent-route")
    assert response.status_code == 404


def test_record_success(client, monkeypatch):  # pylint: disable=redefined-outer-name
    """
    Test the success of the /record route, which processes an audio file,
    sends it to the ML client for transcription, and stores the result in MongoDB.
    """
    wav_file_path = Path(__file__).parent / "wav_example.wav"
    with open(wav_file_path, "rb") as f:
        audio_content = io.BytesIO(f.read())
    audio_content.name = "test_audio.wav"

    def mock_ml_post(*args, **kwargs):  # pylint: disable=unused-argument
        class MockResponse: # pylint: disable=too-few-public-methods
            """Mock the response to include a .json() method"""

            def json(self):
                """.json method"""
                return {"status": "success", "id": "64a1b2c3d4e5f6a7b8c9d0e1"}

        return MockResponse()

    def mock_find_one(query, fields=None):  # pylint: disable=unused-argument
        """
        Mock the MongoDB 'find_one' method.
        Returns a mock result containing the _id from the query.
        """
        return {"_id": query["_id"]}

    monkeypatch.setattr("requests.post", mock_ml_post)
    monkeypatch.setattr("pymongo.collection.Collection.find_one", mock_find_one)
    response = client.post(
        "/record",
        data={"audio": (audio_content, "test_audio.wav")},
        content_type="multipart/form-data",
    )

    # Parse the response JSON
    response_data = response.get_json()
    assert response.status_code == 200
    assert response_data["status"] == "success"
