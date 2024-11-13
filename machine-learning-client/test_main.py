"""
Unit tests for main.py sound classification functions.
"""

from unittest import mock
import numpy as np
from main import (
    extract_features,
    train_model,
    load_model,
    classify_sound,
)


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
@mock.patch("main.os.listdir")
@mock.patch("main.librosa.load")
@mock.patch("main.pickle.dump")
def test_train_model(mock_pickle, mock_load, mock_listdir, mock_exists):
    """Test that train_model calls pickle.dump to save the model."""
    # Mock the file structure and audio loading
    mock_exists.return_value = True
    mock_listdir.return_value = [
        "file1.wav",
        "file2.wav",
    ]  # Simulate files in each label directory
    mock_load.return_value = (
        np.zeros(88200),
        44100,
    )  # Simulate audio data and sample rate

    train_model()
    assert mock_pickle.called


# Test load_model
@mock.patch("main.os.path.exists")
@mock.patch("main.pickle.load")
@mock.patch("main.train_model")
def test_load_model(mock_train_model, mock_pickle_load, mock_exists):
    """Test that load_model loads a model if it exists, otherwise trains a new one."""
    mock_exists.side_effect = [False, True]
    mock_pickle_load.return_value = mock.Mock()
    mock_train_model.return_value = None
    model = load_model()
    assert model is not None
    assert mock_train_model.called or mock_pickle_load.called


# Test classify_sound
def test_classify_sound():
    """Test that classify_sound returns the correct label."""
    model_mock = mock.Mock()
    model_mock.predict.return_value = [0]
    features = np.zeros(40)
    label = classify_sound(model_mock, features)
    assert label == "clapping"
