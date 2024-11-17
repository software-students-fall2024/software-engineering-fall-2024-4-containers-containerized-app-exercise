import os
import pytest
import logging
from unittest.mock import patch, MagicMock
from src.main import main, setup_logging


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Fixture to mock environment variables for the tests.
    """
    monkeypatch.setenv("MONGO_URI", "mongodb://mock_uri")
    monkeypatch.setenv("AUDIO_DIR", "./mock_audio")


@patch("src.main.MongoClient")
@patch("src.main.get_audio_files", return_value=[])
def test_main_no_audio_files(mock_get_audio_files, mock_mongo_client, mock_env_vars, caplog):
    """
    Test `main` function when no audio files are found in the directory.
    """
    del mock_mongo_client  # Unused mock to satisfy pylint
    with caplog.at_level(logging.INFO):
        main()
    assert "There are no audio files in the directory." in caplog.text


@patch("src.main.get_audio_files", return_value=["file1.wav"])
@patch("src.main.transcribe_audio", return_value="Hello world")
@patch("src.main.analyze_sentiment", return_value={"polarity": 0.5, "subjectivity": 0.6, "mood": "Positive"})
@patch("src.main.store_data")
@patch("src.main.MongoClient")
def test_main_with_audio_files(mock_mongo_client, mock_store_data, mock_analyze_sentiment, mock_transcribe_audio, mock_get_audio_files, mock_env_vars):
    """
    Test `main` function when audio files are processed successfully.
    """
    mock_collection = MagicMock()
    mock_mongo_client.return_value.__getitem__.return_value = mock_collection

    main()

    mock_get_audio_files.assert_called_once()
    mock_transcribe_audio.assert_called_once_with("file1.wav")
    mock_analyze_sentiment.assert_called_once_with("Hello world")
    mock_store_data.assert_called_once()


def test_setup_logging(caplog):
    """
    Test `setup_logging` function to ensure logs are properly set up.
    """
    setup_logging()
    with caplog.at_level(logging.INFO):
        logging.getLogger().info("Test log message")
    assert "Test log message" in caplog.text
