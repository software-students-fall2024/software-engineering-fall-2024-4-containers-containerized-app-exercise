"""
test_tests_ml_client.py
"""

import io
from unittest.mock import patch, MagicMock
import pytest
import numpy as np
import warnings
from ..ml_client import encode_face_image

warnings.filterwarnings("ignore", category=DeprecationWarning, module="face_recognition_models")

# Helper function to create a fake image file
def create_fake_image_file():
    """
    Helper function to create a fake image file
    """
    # Create a simple byte stream that mimics an image file
    return io.BytesIO(b"fake image data")

@patch('face_recognition.load_image_file')
@patch('face_recognition.face_encodings')
def test_encode_face_image_success(mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function for successful encoding
    """
    # Mock the face_encodings to return a known value
    mock_face_encodings.return_value = [np.zeros((128,))]

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert error is None
    assert isinstance(encoding, np.ndarray)
    assert np.array_equal(encoding, np.zeros((128,)))

@patch('face_recognition.load_image_file')
@patch('face_recognition.face_encodings')
def test_encode_face_image_no_face_detected(mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function when no face is detected
    """
    # Mock the face_encodings to return an empty list
    mock_face_encodings.return_value = []

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "No face detected in the image."

@patch('face_recognition.load_image_file')
@patch('face_recognition.face_encodings')
def test_encode_face_image_exception(mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function for exception handling
    """
    # Mock load_image_file to raise an exception
    mock_load_image_file.side_effect = Exception("Test Exception")

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "Error during face encoding."