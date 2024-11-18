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
    with patch(
        "machine_learning_client.ml_client.emotion_data_collection"
    ) as mock_collection:
        yield mock_collection


# Mock for TensorFlow model
@pytest.fixture
def mock_model():
    """
    Mock for TensorFlow model.
    """
    with patch("machine_learning_client.ml_client.model") as model_mock:
        model_mock.predict.return_value = np.array(
            [[0.8, 0.1, 0.05, 0.03, 0.02]]
        )  # Predicts "Happy 😊"
        yield model_mock


def test_detect_emotion(client, mock_model, mock_db):
    mock_model.predict.return_value = np.array([[0.8, 0.1, 0.05, 0.03, 0.02]])  # Predicts "Happy 😊"

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["emotion"] == "Happy 😊"



def test_invalid_image_input(client):
    # Send an invalid image
    response = client.post(
        "/detect_emotion",
        data={"image": "not_a_valid_image"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data
    assert response_data["error"] == "No image file provided"



def test_model_prediction_error(client, mock_model):
    mock_model.predict.side_effect = Exception("Model prediction failed")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Model prediction failed" in response_data["error"]



def test_detect_emotion_invalid_method(client):
    """
    Test the /detect_emotion route with an invalid method (GET instead of POST).
    """
    response = client.get("/detect_emotion")
    assert response.status_code == 405  # Method Not Allowed


def test_database_insertion_error(client, mock_model, mock_db):
    mock_db.insert_one.side_effect = Exception("Database insertion failed")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Database insertion failed" in response_data["error"]


def test_missing_content_type(client):
    """
    Test the /detect_emotion route with missing Content-Type header.
    """
    response = client.post("/detect_emotion", data={})
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data
    assert response_data["error"] == "No image file provided"


def test_invalid_route(client):
    """
    Test accessing an invalid route.
    """
    response = client.get("/non_existent_route")
    assert response.status_code == 404  # Not Found


def test_invalid_method_on_detect_emotion(client):
    """
    Test the /detect_emotion route with an invalid HTTP method (GET).
    """
    response = client.get("/detect_emotion")
    assert response.status_code == 405  # Method Not Allowed


def test_mongodb_insertion_error(client, mock_model, mock_db):
    """
    Test the /detect_emotion route when MongoDB insertion fails.
    """
    mock_db.insert_one.side_effect = Exception("Database insertion failed")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Database insertion failed" in response_data["error"]


def test_alternative_emotion_prediction(client, mock_model, mock_db):
    """
    Test the /detect_emotion route when the model predicts "Sad 😢".
    """
    mock_model.predict.return_value = np.array(
        [[0.1, 0.8, 0.05, 0.03, 0.02]]
    )  # Predicts "Sad 😢"

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["emotion"] == "Sad 😢"
    mock_db.insert_one.assert_called_once()


def test_model_not_loaded(client, mock_db):
    """
    Test the /detect_emotion route when the TensorFlow model is not loaded.
    """
    with patch(
        "machine_learning_client.ml_client.model", None
    ):  # Simulate missing model
        # Create a dummy image
        dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
        _, buffer = cv2.imencode(".jpg", dummy_image)
        dummy_image_data = buffer.tobytes()

        file_storage = FileStorage(
            stream=BytesIO(dummy_image_data),
            filename="test_image.jpg",
            content_type="image/jpeg",
        )

        response = client.post(
            "/detect_emotion",
            data={"image": file_storage},
            content_type="multipart/form-data",
        )

        assert response.status_code == 500
        response_data = response.get_json()
        assert "error" in response_data
        assert "NoneType" in response_data["error"]  # Error due to model being None


def test_unhandled_exception_in_prediction(client, mock_model):
    """
    Test the /detect_emotion route when an unhandled exception occurs during model prediction.
    """
    mock_model.predict.side_effect = Exception("Unexpected error during prediction")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Unexpected error during prediction" in response_data["error"]


def test_valid_prediction_with_mongodb_error(client, mock_model, mock_db):
    """
    Test the /detect_emotion route with valid prediction but MongoDB insertion fails.
    """
    mock_model.predict.return_value = np.array(
        [[0.8, 0.1, 0.05, 0.03, 0.02]]
    )  # Predicts "Happy 😊"
    mock_db.insert_one.side_effect = Exception("Database insertion error")

    # Create a dummy image
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    dummy_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(dummy_image_data),
        filename="test_image.jpg",
        content_type="image/jpeg",
    )

    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Database insertion error" in response_data["error"]
