"""
Unit tests for main.py sound classification functions.
"""

from unittest import mock
import numpy as np
from main import (
    record_audio,
    extract_features,
    train_model,
    load_model,
    classify_sound,
)


# Test record_audio
@mock.patch("main.sd.rec")
def test_record_audio(mock_rec):
    """Test that record_audio function returns the correct shape."""
    mock_rec.return_value = np.zeros((88200, 1), dtype="float32")
    audio = record_audio(duration=2, fs=44100)
    assert audio.shape == (88200,)


# Test extract_features
@mock.patch("main.librosa.feature.mfcc")
def test_extract_features(mock_mfcc):
    """Test that extract_features returns the correct feature shape."""
    mock_mfcc.return_value = np.zeros((40, 87))
    audio = np.zeros(88200, dtype="float32")
    fs = 44100
    features = extract_features(audio, fs)
    assert features.shape == (40,)


# Test train_model
@mock.patch("main.os.path.exists")
@mock.patch("main.librosa.load")
@mock.patch("main.pickle.dump")
def test_train_model(mock_pickle, mock_load, mock_exists):
    """Test that train_model calls pickle.dump to save the model."""
    mock_exists.return_value = True
    mock_load.return_value = (np.zeros(88200), 44100)
    train_model()
    assert mock_pickle.called


# Test load_model
@mock.patch("main.os.path.exists")
@mock.patch("main.pickle.load")
def test_load_model(mock_pickle_load, mock_exists):
    """Test that load_model loads a model if it exists."""
    mock_exists.return_value = True
    mock_pickle_load.return_value = mock.Mock()
    model = load_model()
    assert model is not None


# Test classify_sound
def test_classify_sound():
    """Test that classify_sound returns the correct label."""
    model_mock = mock.Mock()
    model_mock.predict.return_value = [0]
    features = np.zeros(40)
    label = classify_sound(model_mock, features)
    assert label == "clapping"
