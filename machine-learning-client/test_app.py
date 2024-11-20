"""
This module contains tests for the ML client. Run with 'pipenv run pytest'
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

from io import BytesIO
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image
import numpy as np

from app import app, detect_objects


@pytest.fixture
def flask_test_client():
    """Fixture for Flask test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def mongo_mock(monkeypatch):
    """Mock MongoDB operations."""
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client["object_detection"]["detected_objects"] = mock_collection
    monkeypatch.setattr("app.client", mock_client)
    monkeypatch.setattr(
        "app.collection", mock_collection
    )  # Ensure collection is mocked
    return mock_collection


@pytest.fixture
def model_mock(monkeypatch):
    """Mock YOLOv5 model."""
    mock_model_instance = MagicMock()
    mock_results = MagicMock()
    mock_results.pandas.return_value.xyxy = [
        MagicMock(to_dict=lambda orient: [{"name": "cat", "confidence": 0.9}])
    ]
    mock_model_instance.return_value = mock_results
    monkeypatch.setattr("torch.hub.load", lambda *args, **kwargs: mock_model_instance)
    monkeypatch.setattr("app.model", mock_model_instance)
    return mock_model_instance


def test_index(flask_test_client):  # pylint: disable=redefined-outer-name
    """Test the health check endpoint."""
    response = flask_test_client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"status": "running"}


def test_detect_objects(
    model_mock,
):  # pylint: disable=redefined-outer-name, unused-argument
    """Test the detect_objects function."""
    mock_image = Image.fromarray(np.zeros((480, 640, 3), dtype=np.uint8))
    detections = detect_objects(mock_image)

    assert len(detections) == 1
    assert detections[0]["label"] == "cat"
    assert detections[0]["confidence"] == 0.9


def test_process_pending_no_document(
    flask_test_client, mongo_mock
):  # pylint: disable=redefined-outer-name
    """Test the /process_pending endpoint with no pending document."""
    mongo_mock.find_one.return_value = None

    response = flask_test_client.post("/process_pending")
    assert response.status_code == 404
    assert response.get_json() == {"message": "No pending frames to process"}


def test_process_pending_with_document(
    flask_test_client, mongo_mock, model_mock
):  # pylint: disable=redefined-outer-name, unused-argument
    """Test the /process_pending endpoint with a pending document."""
    # Mock a pending document
    mock_image_data = BytesIO()
    mock_image = Image.fromarray(np.zeros((480, 640, 3), dtype=np.uint8))
    mock_image.save(mock_image_data, format="JPEG")
    mock_image_data.seek(0)

    mongo_mock.find_one.return_value = {
        "_id": "mock_id",
        "status": "pending",
        "image": mock_image_data.getvalue(),
    }

    mongo_mock.update_one.return_value = None

    fixed_now = datetime(2024, 11, 20, 3, 5, 6, tzinfo=timezone.utc)
    with patch("app.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.timezone = timezone

        response = flask_test_client.post("/process_pending")
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["message"] == "Frame processed"
        assert len(response_data["detections"]) == 1
        assert response_data["detections"][0]["label"] == "cat"
        assert response_data["detections"][0]["confidence"] == 0.9

        mongo_mock.find_one.assert_called_once_with({"status": "pending"})
        mongo_mock.update_one.assert_called_once_with(
            {"_id": "mock_id"},
            {
                "$set": {
                    "status": "processed",
                    "detections": [{"label": "cat", "confidence": 0.9}],
                    "processed_at": fixed_now,
                }
            },
        )
