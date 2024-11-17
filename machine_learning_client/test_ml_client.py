import pytest
from unittest.mock import MagicMock, patch
from machine_learning_client.ml_client import detect_emotion, emotion_data_collection
import numpy as np
# Import OpenCV for image processing
import cv2


# Mock the MongoDB collection
@pytest.fixture
def mock_db():
    with patch("machine_learning_client.ml_client.emotion_data_collection") as mock_collection:
        yield mock_collection

# Mock the model prediction
@pytest.fixture
def mock_model():
    with patch("machine_learning_client.ml_client.model") as mock_model:
        mock_model.predict.return_value = np.array([[0.8, 0.1, 0.05, 0.03, 0.02]])  # Simulates "Happy 😊"
        yield mock_model

def test_detect_emotion(mock_db, mock_model):
    # Create a dummy image frame (48x48 grayscale)
    dummy_frame = np.ones((48, 48, 3), dtype=np.uint8) * 255  # White image for testing
    dummy_frame = cv2.resize(dummy_frame, (48, 48))
    dummy_frame = cv2.cvtColor(dummy_frame, cv2.COLOR_BGR2GRAY)

    # Call the function
    emotion = detect_emotion(dummy_frame)

    # Check the returned emotion
    assert emotion == "Happy 😊"  # Matches the mocked prediction

    # Check that a new entry was added to the database
    mock_db.insert_one.assert_called_once()
    call_args = mock_db.insert_one.call_args[0][0]
    assert call_args["emotion"] == "Happy 😊"
    assert "timestamp" in call_args

def test_invalid_image_input(mock_model):
    # Test with invalid input (e.g., empty array)
    with pytest.raises(Exception):
        detect_emotion(np.array([]))

def test_model_error(mock_model):
    # Simulate a model prediction error
    mock_model.predict.side_effect = Exception("Model prediction failed")

    # Test with valid input
    dummy_frame = np.ones((48, 48, 1), dtype=np.uint8)
    dummy_frame = dummy_frame / 255.0  # Normalize

    with pytest.raises(Exception, match="Model prediction failed"):
        detect_emotion(dummy_frame)

