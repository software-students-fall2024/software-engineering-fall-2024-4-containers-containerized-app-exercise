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
    # Mock the existence of the training_data directory
    mock_exists.return_value = True
    # Mock the list of files in each label directory
    mock_listdir.return_value = ["file1.wav", "file2.wav"]
    # Mock the audio loading process
    mock_load.return_value = (np.zeros(88200), 44100)
    
    train_model()
    assert mock_pickle.called


# Test load_model
@mock.patch("main.os.path.exists")
@mock.patch("main.pickle.load")
@mock.patch("main.pickle.dump")
@mock.patch("main.os.listdir")
@mock.patch("main.librosa.load")
def test_load_model(mock_pickle_load, mock_exists, mock_pickle, mock_listdir, mock_load):
    """Test that load_model loads a model if it exists."""
    # Mock the existence of the model file
    mock_exists.side_effect = [False, True]  # First call (model not found) triggers train_model; second call (model found)
    # Mock the list of files and audio loading for train_model
    mock_listdir.return_value = ["file1.wav", "file2.wav"]
    mock_load.return_value = (np.zeros(88200), 44100)
    mock_pickle.return_value = None  # Mock saving process in train_model

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
