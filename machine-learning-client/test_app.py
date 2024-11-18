"""
This module contains tests for the ML client. Run with 'pipenv run pytest' 
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

from unittest import mock
from unittest.mock import patch, MagicMock
from io import BytesIO
import pytest
from PIL import Image
from app import app, detect_objects

app.config["TESTING"] = True


@pytest.fixture(name="test_client")
def fixture_test_client():
    """Fixture for Flask test client."""
    with app.test_client() as client:
        yield client


@patch("app.model")
def test_detect_objects_returns_correct_predictions(mock_model):
    """Test detect_objects with mocked YOLOv5 predictions."""
    # mock YOLOv5 output
    mock_results = MagicMock()
    mock_results.pandas.return_value.xyxy = [
        MagicMock(
            to_dict=MagicMock(
                return_value=[
                    {"name": "person", "confidence": 0.98},
                    {"name": "cat", "confidence": 0.85},
                ]
            )
        )
    ]
    mock_model.return_value = mock_results

    # create a blank image
    image = Image.new("RGB", (224, 224), color="white")

    detected_objects = detect_objects(image)

    # Validate the result
    assert detected_objects == [
        {"label": "person", "confidence": 0.98},
        {"label": "cat", "confidence": 0.85},
    ]


def test_detect_route_returns_error_on_missing_file(test_client):
    """Test /api/detect returns 400 when no file is provided."""
    response = test_client.post("/api/detect")
    assert response.status_code == 400
    assert "No image file provided." in response.get_data(as_text=True)


@patch("app.detect_objects")
def test_detect_route_with_valid_file(mock_detect_objects, test_client):
    """Test /api/detect returns predictions for valid file uploads."""
    # Mock detect_objects response
    mock_detect_objects.return_value = [
        {"label": "person", "confidence": 0.98},
        {"label": "cat", "confidence": 0.85},
    ]

    # create a blank image and save to buffer
    image = Image.new("RGB", (224, 224), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # send POST request
    response = test_client.post(
        "/api/detect",
        content_type="multipart/form-data",
        data={"file": (buffer, "test.png")},
    )

    # validate response
    assert response.status_code == 200
    assert response.get_json() == {
        "timestamp": mock.ANY, 
        "detected_objects": [
            {"label": "person", "confidence": 0.98},
            {"label": "cat", "confidence": 0.85},
        ],
    }



def test_encode_image():
    """Test base64 encoding of an image."""
    # create a sample blank image
    image = Image.new("RGB", (100, 100), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded_image = buffer.getvalue()

    assert isinstance(encoded_image, bytes)
    assert len(encoded_image) > 0
