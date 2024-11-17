"""
Test module for emotion detector functionality.
This module contains unit tests for the EmotionDetector class.
"""

import cv2
import numpy as np
from emotion_detector import EmotionDetector


def test_emotion_detector_initialization():
    """Test if EmotionDetector can be properly initialized."""
    detector = EmotionDetector()
    assert detector is not None


def test_emotion_detection_with_valid_image():
    """Test emotion detection with a valid image containing a face."""
    detector = EmotionDetector()
    img = cv2.imread("tests/images/test_face.jpg")
    if img is not None:
        result = detector.detect_emotion(img)
        assert "status" in result
        assert "emotions" in result
        assert isinstance(result["emotions"], dict)


def test_emotion_detection_with_no_face():
    """Test emotion detection with an image containing no face."""
    detector = EmotionDetector()
    # Create a blank image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = detector.detect_emotion(img)
    assert "error" in result
