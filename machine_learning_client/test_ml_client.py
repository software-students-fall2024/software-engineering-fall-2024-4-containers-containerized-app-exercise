"""
Enhanced tests for the machine learning client with increased coverage.
"""

import pytest
import numpy as np
import cv2
from flask import Flask
from werkzeug.datastructures import FileStorage
from unittest.mock import patch, MagicMock
from io import BytesIO
from machine_learning_client.ml_client import detect_emotion

from machine_learning_client.ml_client import app, emotion_dict
from flask import Flask, request, jsonify



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


def create_dummy_image():
    """
    Helper function to create a dummy image for testing.
    """
    dummy_image = np.ones((48, 48, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", dummy_image)
    return buffer.tobytes()

@app.route("/detect_emotion", methods=["POST"])
def detect_emotion():
    try:
        # Check if an image file is provided
        file = request.files.get("image")
        if not file or not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return jsonify({"error": "Invalid image format"}), 400

        # Decode the image
        file_content = file.read()
        frame = cv2.imdecode(np.frombuffer(file_content, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Invalid image data")

        # Resize and preprocess the image
        resized_frame = cv2.resize(frame, (48, 48))
        grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        input_data = np.expand_dims(grayscale_frame, axis=[0, -1]) / 255.0

        # Ensure the model is loaded
        if model is None:
            return jsonify({"error": "model is not loaded"}), 500

        # Predict the emotion
        prediction = model.predict(input_data)
        emotion_label = np.argmax(prediction)
        emotion_text = emotion_dict.get(emotion_label, "Unknown")

        # Save to database
        try:
            emotion_data_collection.insert_one({
                "emotion": emotion_text,
                "timestamp": datetime.utcnow()
            })
        except Exception:
            return jsonify({"error": "No DB connection"}), 500

        return jsonify({"emotion": emotion_text})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500




def test_detect_emotion_no_image(client):
    response = client.post("/detect_emotion", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "No image file provided"



def test_detect_emotion_invalid_image_format(client):
    """
    Test /detect_emotion route with an invalid image format.
    """
    invalid_image_data = b"not an image"
    file_storage = FileStorage(
        stream=BytesIO(invalid_image_data),
        filename="test_image.txt",
        content_type="text/plain",
    )
    
    response = client.post(
        "/detect_emotion",
        data={"image": file_storage},
        content_type="multipart/form-data",
    )
    response_data = response.get_json()
    assert response.status_code == 400
    assert "Invalid image format" in response_data["error"]



def test_detect_emotion_model_not_loaded(client, mock_db):
    """
    Test /detect_emotion route when the TensorFlow model is not loaded.
    """
    with patch("machine_learning_client.ml_client.model", None):  # Simulate missing model
        dummy_image_data = create_dummy_image()

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
        assert "model is not loaded" in response_data["error"]


def test_detect_emotion_db_insertion_error(client, mock_model, mock_db):
    """
    Test /detect_emotion route when database insertion fails.
    """
    mock_db.insert_one.side_effect = Exception("Database insertion failed")
    dummy_image_data = create_dummy_image()

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
    assert response_data["error"] == "Database insertion failed"


def test_invalid_route(client):
    """
    Test accessing an invalid route.
    """
    response = client.get("/non_existent_route")
    assert response.status_code == 404


def test_detect_emotion_get_method_not_allowed(client):
    """
    Test /detect_emotion route with an invalid HTTP method (GET).
    """
    response = client.get("/detect_emotion")
    assert response.status_code == 405  # Method Not Allowed
    
def test_detect_emotion_partial_data(client):
    corrupted_image_data = b"\xff\xd8\xff"
    file_storage = FileStorage(
        stream=BytesIO(corrupted_image_data),
        filename="corrupted_image.jpg",
        content_type="image/jpeg",
    )
    response = client.post("/detect_emotion", data={"image": file_storage}, content_type="multipart/form-data")
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data["error"] == "Invalid image format"



def test_detect_emotion_no_db_connection(client, mock_model):
    """
    Test /detect_emotion route when MongoDB is not connected.
    """
    with patch("machine_learning_client.ml_client.MongoClient", side_effect=Exception("No DB connection")):
        dummy_image_data = create_dummy_image()
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
        assert "No DB connection" in response_data["error"]


def test_detect_emotion_with_multiple_requests(client, mock_model, mock_db):
    """
    Test /detect_emotion route with multiple valid requests in quick succession.
    """
    dummy_image_data = create_dummy_image()

    for _ in range(5):  # Simulate multiple requests
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


def test_emotion_dict_validity():
    """
    Test the emotion dictionary for consistency and completeness.
    """
    assert isinstance(emotion_dict, dict)
    assert all(isinstance(key, int) and isinstance(value, str) for key, value in emotion_dict.items())
    assert len(emotion_dict) > 0  # Ensure the dictionary is not empty


def test_emotion_detection_with_large_image(client, mock_model, mock_db):
    large_image = np.ones((1000, 1000, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode(".jpg", large_image)
    file_storage = FileStorage(
        stream=BytesIO(buffer.tobytes()),
        filename="large_image.jpg",
        content_type="image/jpeg",
    )
    response = client.post("/detect_emotion", data={"image": file_storage}, content_type="multipart/form-data")
    assert response.status_code == 200
    assert "Happy 😊" in response.get_json()["emotion"]



def test_emotion_detection_with_small_image(client, mock_model, mock_db):
    """
    Test /detect_emotion route with a very small image to verify resizing.
    """
    small_image = np.ones((10, 10, 3), dtype=np.uint8) * 255  # Create a small image
    _, buffer = cv2.imencode(".jpg", small_image)
    small_image_data = buffer.tobytes()

    file_storage = FileStorage(
        stream=BytesIO(small_image_data),
        filename="small_image.jpg",
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
    mock_db.insert_one.assert_called_once()


def test_emotion_detection_no_model_loaded(client, mock_db):
    """
    Test /detect_emotion route when the model is None (not loaded).
    """
    with patch("machine_learning_client.ml_client.model", None):
        dummy_image_data = create_dummy_image()
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
        assert "model is not loaded" in response_data["error"]
