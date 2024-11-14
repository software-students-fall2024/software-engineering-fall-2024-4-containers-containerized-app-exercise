import pytest
import ml_client
import numpy as np


def test_encode_face():
    encoding, error = ml_client.encode_face(
        "test_image.jpg"
    )  # Use a valid image path for testing
    if error:
        assert encoding is None
    else:
        assert encoding is not None
        assert isinstance(encoding, np.ndarray)


def test_recognize_face():
    stored_encodings = [np.zeros((128,))]  # Example stored encoding
    result, error = ml_client.recognize_face(stored_encodings)
    assert result in ["verified", "not verified"]
    assert error is None


def test_save_metadata():
    encoding = np.zeros((128,)).tolist()  # Example encoding
    metadata = {
        "source": "test",
        "timestamp": "2024-11-13T15:00:00",
        "notes": "Test metadata",
    }
    ml_client.save_metadata(encoding, metadata)
    # Check that the data was inserted into the database
    user = ml_client.users_collection.find_one({"metadata.notes": "Test metadata"})
    assert user is not None
