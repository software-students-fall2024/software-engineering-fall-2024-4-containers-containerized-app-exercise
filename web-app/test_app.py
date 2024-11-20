"""
This module contains tests for the Web App. Run with 'python -m
pytest test_app.py'
or to see with coverage run with
'python -m pytest --cov=app test_app.py'
"""

from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import pytest
from bson import ObjectId
from app import app


@pytest.fixture(name="test_client")
def fixture_test_client():
    """Mock client fixture"""
    with app.test_client() as client:
        yield client


@pytest.fixture
def mongo_mock(monkeypatch):
    """Mock MongoDB operations."""
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client["object_detection"]["detected_objects"] = mock_collection
    monkeypatch.setattr("app.client", mock_client)
    monkeypatch.setattr("app.collection", mock_collection)
    return mock_collection


@pytest.fixture
def camera_mock(monkeypatch):
    """Mock camera operations."""
    mock_camera = MagicMock()
    monkeypatch.setattr("app.camera", mock_camera)
    return mock_camera


@pytest.fixture
def requests_mock(monkeypatch):
    """Mock requests.post for the ML app."""
    mock_post = MagicMock()
    monkeypatch.setattr("requests.post", mock_post)
    return mock_post


def test_index_page(
    test_client,
):  # Use 'client' as the argument name to match the fixture
    """Test the index page route."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Real-Time Object Detection" in response.data


def test_capture_and_process_success( # pylint: disable=redefined-outer-name
    test_client, mongo_mock, camera_mock, requests_mock
):
    """Test /capture_and_process with successful processing."""
    camera_mock.read.return_value = (True, b"mock_frame")

    with patch("cv2.imencode", return_value=(True, b"mock_encoded_frame")):
        requests_mock.return_value.status_code = 200
        requests_mock.return_value.json.return_value = {
            "detections": [{"label": "cat", "confidence": 0.95}]
        }

        mock_insert_result = MagicMock(inserted_id=ObjectId())
        mongo_mock.insert_one.return_value = mock_insert_result

        response = test_client.post("/capture_and_process")
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["message"] == "Frame captured and processed"
        assert "id" in response_data
        assert len(response_data["detections"]) == 1
        assert response_data["detections"][0]["label"] == "cat"


def test_capture_and_process_ml_failure( # pylint: disable=redefined-outer-name,unused-argument
    test_client, mongo_mock, camera_mock, requests_mock
):
    """Test /capture_and_process when ML app fails."""
    camera_mock.read.return_value = (True, b"mock_frame")

    with patch("cv2.imencode", return_value=(True, b"mock_encoded_frame")):
        requests_mock.return_value.status_code = 500
        response = test_client.post("/capture_and_process")
        assert response.status_code == 500
        assert response.get_json() == {"error": "Processing failed"}


def test_latest_detection_with_data(test_client, mongo_mock): # pylint: disable=redefined-outer-name
    """Test /latest_detection with available processed data."""
    mock_detection = {
        "timestamp": datetime(2024, 11, 20, 3, 5, 6, tzinfo=timezone.utc).isoformat(),
        "detections": [{"label": "dog", "confidence": 0.89}],
    }
    mongo_mock.find_one.return_value = mock_detection

    response = test_client.get("/latest_detection")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["timestamp"] == mock_detection["timestamp"]
    assert response_data["labels"] == mock_detection["detections"]


def test_video_feed(test_client, camera_mock): # pylint: disable=redefined-outer-name
    """Test /video_feed route."""
    camera_mock.read.side_effect = [(True, b"frame1"), (True, b"frame2"), (False, None)]

    with patch("cv2.imencode", return_value=(True, b"mock_encoded_frame")):
        response = test_client.get("/video_feed")
        assert response.status_code == 200
        assert response.content_type == "multipart/x-mixed-replace; boundary=frame"
