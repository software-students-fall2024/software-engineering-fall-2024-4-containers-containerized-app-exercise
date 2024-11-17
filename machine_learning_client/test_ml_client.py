"""
Tests for the machine learning client.
"""
from unittest.mock import patch
import pytest
import numpy as np
import cv2  # Import OpenCV for image processing
from machine_learning_client.ml_client import detect_emotion

# Mock the MongoDB collection
@pytest.fixture
def mock_db():
    """
    Fixture to mock the MongoDB collection.
    """
    with patch("machine_learning_client.ml_client.emotion_data_collection") as mock_collection:
        yield mock_collection


@pytest.fixture
def mock_model():
    """
    Fixture to mock the emotion detection model.
    """
    with patch("machine_learning_client.ml_client.model") as model_mock:
        model_mock.predict.return_value = np.array([[0.8, 0.1, 0.05, 0.03, 0.02]])
        yield model_mock


# Test for detect_emotion route with valid input
def test_detect_emotion(client, monkeypatch):
    """
    Test the /detect_emotion route with a valid image.
    """
    def mock_predict(input_data):
        return np.array([[0.8, 0.1, 0.05, 0.03, 0.02]])  # Simulates "Happy 😊"

    def mock_insert_one(data):
        pass  # Mock insertion to MongoDB

    # Mock the model's predict method and MongoDB insertion
    monkeypatch.setattr("machine_learning_client.ml_client.model.predict", mock_predict)
    monkeypatch.setattr(
        "machine_learning_client.ml_client.emotion_data_collection.insert_one",
        mock_insert_one,
    )

    # Simulate sending an image as part of the POST request
    image_data = np.ones((48, 48, 3), dtype=np.uint8)  # Dummy white image
    _, buffer = cv2.imencode(".jpg", image_data)
    response = client.post(
        "/detect_emotion",
        data={"image": (buffer.tobytes(), "test.jpg")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json["emotion"] == "Happy 😊"

def test_invalid_image_input():
    """
    Test the detect_emotion function with invalid input.
    """
    # Test with invalid input (e.g., empty array)
    with pytest.raises(ValueError, match="Invalid input image"):
        detect_emotion(np.array([]))


def test_model_error(mock_model):
    """
    Test the detect_emotion function when the model fails.
    """
    # Simulate a model prediction error
    mock_model.predict.side_effect = Exception("Model prediction failed")

    # Test with valid input
    dummy_frame = np.ones((48, 48, 1), dtype=np.uint8)
    normalized_frame = dummy_frame / 255.0  # Normalize

    with pytest.raises(Exception, match="Model prediction failed"):
        detect_emotion(normalized_frame)