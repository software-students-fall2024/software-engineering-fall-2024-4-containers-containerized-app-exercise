"""
This module contains tests for the ML client. Run with 'python -m pytest test_app.py' 
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import base64
import numpy as np
import pytest
import tensorflow as tf
from io import BytesIO
from app import app, preprocess_image, detect_objects, encode_image
from flask import json
from unittest.mock import patch, Mock

# Configure the app for testing
app.config["TESTING"] = True


@pytest.fixture
def client():
    """Flask client for testing."""
    with app.test_client() as client:
        yield client


def test_preprocess_image():
    """Test image preprocessing for MobileNet input."""
    # Create a sample random image tensor
    image = tf.random.uniform(shape=(500, 500, 3), minval=0, maxval=255, dtype=tf.int32)
    image = tf.cast(image, tf.float32)  # Convert to float32
    preprocessed_image = preprocess_image(image)

    # Check the preprocessed image shape and type
    assert preprocessed_image.shape == (1, 224, 224, 3)
    assert preprocessed_image.dtype == np.float32


@patch("app.model.predict")
def test_detect_objects(mock_predict):
    """Test object detection using mocked MobileNet predictions."""
    # Mock MobileNet's predict output
    mock_predict.return_value = np.random.rand(1, 1000)  # Simulate a prediction output
    image = tf.random.uniform(shape=(224, 224, 3), minval=0, maxval=255, dtype=tf.int32)
    image = tf.cast(image, tf.float32)  # Convert to float32

    # Run detection
    detected_objects = detect_objects(image)

    # Assertions
    assert isinstance(detected_objects, list)
    assert len(detected_objects) == 3  # Should return top 3 predictions
    for obj in detected_objects:
        assert "label" in obj
        assert "confidence" in obj


def test_encode_image():
    """Test image encoding to base64."""
    # Create a sample blank image
    image = np.zeros((100, 100, 3), np.uint8)
    encoded_image = encode_image(image)

    # Check that the encoding result is a string and not empty
    assert isinstance(encoded_image, str)
    assert len(encoded_image) > 0


def test_detect_route_no_file(client):
    """Test /api/detect route when no file is provided."""
    response = client.post("/api/detect")
    data = response.get_data(as_text=True)

    # Check response status code and message
    assert response.status_code == 400
    assert "No image file provided." in data


@patch("app.detect_objects")
def test_detect_route_with_file(mock_detect_objects, client):
    """Test /api/detect route with a valid image file."""
    ## TODO