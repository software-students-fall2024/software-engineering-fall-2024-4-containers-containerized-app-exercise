# test_ml_client.py
import pytest
from ml_client import detect_emotion
from datetime import datetime
import cv2
import numpy as np

# Mocked database and model setup can be added here if needed

def test_detect_emotion():
    # Create a dummy image frame (48x48 grayscale)
    dummy_frame = np.ones((48, 48, 3), dtype=np.uint8) * 255  # White image for testing

    # Call the function
    emotion = detect_emotion(dummy_frame)

    # Check that an emotion is returned and is a known label
    assert emotion in ["Happy 😊", "Sad 😢", "Angry 😡", "Surprised 😮", "Neutral 😐"]

    # Optional: Verify that a new entry was added to the database if the database is mocked
