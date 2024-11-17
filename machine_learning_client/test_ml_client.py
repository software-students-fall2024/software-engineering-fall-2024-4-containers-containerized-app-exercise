"""
Tests for the machine learning client.
"""
import pytest
import numpy as np
import cv2
from flask import Flask
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock
from io import BytesIO

from machine_learning_client.ml_client import app, emotion_dict

# Mock the MongoDB collection
@pytest.fixture
def client():
    """
    Fixture to provide a Flask test client for testing routes.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Mock for MongoDB collection
@pytest.fixture
def mock_db():
    """
    Mock for MongoDB collection.
    """
    with patch("machine_learning_client.ml_client.emotion_data_collection") as mock_collection:
        yield mock_collection


# Mock for TensorFlow model
@pytest.fixture
def mock_model():
    """
    Mock for TensorFlow model.
    """
    with patch("machine_learning_client.ml_client.model") as model_mock:
        model_mock.predict.return_value = np.array([[0.8, 0.1, 0.05, 0.03, 0.02]])  # Predicts "Happy 😊"
        yield model_mock


def test_detect_emotion(client, mock_model, mock_db):
    """
    Test the /detect_emotion route with valid input.
    """
    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    # Simulate a file upload using FileStorage
    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    # Send POST request with the image
    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    # Assert successful response
    assert response.status_code == 200
    response_data = response.get_json()
    assert "emotion" in response_data
    assert response_data["emotion"] == "Happy 😊"

    # Assert database insertion
    mock_db.insert_one.assert_called_once()
    db_entry = mock_db.insert_one.call_args[0][0]
    assert db_entry["emotion"] == "Happy 😊"
    assert "timestamp" in db_entry


def test_invalid_image_input(client):
    """
    Test the /detect_emotion route with invalid input.
    """
    # Send POST request without an image
    response = client.post("/detect_emotion", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data
    assert response_data["error"] == "No image file provided"


def test_model_error(client, mock_model):
    """
    Test the /detect_emotion route when the model fails.
    """
    # Simulate a model prediction error
    mock_model.predict.side_effect = Exception("Model prediction failed")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    # Simulate a file upload using FileStorage
    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    # Send POST request with the image
    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    # Assert server error
    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Model prediction failed" in response_data["error"]