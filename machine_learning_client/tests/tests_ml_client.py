"""
Unit tests for the ml_client module.
"""

import io
import warnings
from unittest.mock import patch

import numpy as np
from PIL import UnidentifiedImageError

from ..ml_client import encode_face_image

warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="face_recognition_models"
)


def create_fake_image_file():
    """
    Helper function to create a fake image file.
    """
    # Create a simple byte stream that mimics an image file
    return io.BytesIO(b"fake image data")


@patch("face_recognition.load_image_file")
@patch("face_recognition.face_encodings")
def test_encode_face_image_success(mock_face_encodings, _mock_load_image_file):
    """
    Test the encode_face_image function for successful encoding.
    """
    # Mock the face_encodings to return a known value
    mock_face_encodings.return_value = [np.zeros((128,))]

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert error is None
    assert isinstance(encoding, np.ndarray)
    assert np.array_equal(encoding, np.zeros((128,)))


@patch("face_recognition.load_image_file")
@patch("face_recognition.face_encodings")
def test_encode_face_image_no_face_detected(mock_face_encodings, _mock_load_image_file):
    """
    Test the encode_face_image function when no face is detected.
    """
    # Mock the face_encodings to return an empty list
    mock_face_encodings.return_value = []

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "No face detected in the image."


@patch("face_recognition.load_image_file")
@patch("face_recognition.face_encodings")
def test_encode_face_image_invalid_image(_mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function for invalid image file.
    """
    # Mock load_image_file to raise UnidentifiedImageError
    mock_load_image_file.side_effect = UnidentifiedImageError("Invalid image file")

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "Invalid image file."


@patch("face_recognition.load_image_file")
@patch("face_recognition.face_encodings")
def test_encode_face_image_runtime_error(_mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function for runtime error.
    """
    # Mock load_image_file to raise RuntimeError
    mock_load_image_file.side_effect = RuntimeError("Runtime error")

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "Face recognition error: Runtime error"


@patch("face_recognition.load_image_file")
@patch("face_recognition.face_encodings")
def test_encode_face_image_exception(_mock_face_encodings, mock_load_image_file):
    """
    Test the encode_face_image function for unexpected exception handling.
    """
    # Mock load_image_file to raise an unexpected exception
    mock_load_image_file.side_effect = Exception("Test Exception")

    # Create a fake image file
    fake_image_file = create_fake_image_file()

    encoding, error = encode_face_image(fake_image_file)
    assert encoding is None
    assert error == "Unexpected error: Test Exception"
