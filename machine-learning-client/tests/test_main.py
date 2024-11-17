import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.main import setup_logging, main
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.main import setup_logging, main

class TestMain(unittest.TestCase):
    """Unit tests for the main.py module."""

    @patch("main.MongoClient")
    def test_mongo_connection_success(self, mock_mongo_client):
        """
        Test that the MongoDB connection succeeds without exceptions.
        """
        # Mock the MongoClient to avoid real database calls
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client

        # Mock environment variables
        with patch.dict(os.environ, {"MONGO_URI": "mongodb://mock_uri", "AUDIO_DIR": "./mock_audio"}):
            with patch("main.get_audio_files", return_value=["test.wav"]):
                with patch("main.transcribe_audio", return_value="mock transcript"):
                    with patch("main.analyze_sentiment", return_value={"mood": "Positive"}):
                        with patch("main.store_data") as mock_store_data:
                            main()
                            # Verify store_data is called with the correct arguments
                            mock_store_data.assert_called_once_with(
                                mock_client["voice_mood_journal"]["entries"],
                                {
                                    "file_name": "test.wav",
                                    "transcript": "mock transcript",
                                    "sentiment": {"mood": "Positive"},
                                    "timestamp": unittest.mock.ANY,  # Match datetime
                                },
                            )

    @patch("main.MongoClient")
    def test_mongo_connection_failure(self, mock_mongo_client):
        """
        Test that the MongoDB connection failure is handled correctly.
        """
        # Simulate a MongoDB connection failure
        mock_mongo_client.side_effect = Exception("Connection failed")

        with patch.dict(os.environ, {"MONGO_URI": "mongodb://mock_uri"}):
            with patch("main.get_audio_files") as mock_get_audio_files:
                main()
                # Ensure pipeline doesn't proceed
                mock_get_audio_files.assert_not_called()

    @patch("main.get_audio_files")
    def test_no_audio_files(self, mock_get_audio_files):
        """
        Test that the pipeline exits gracefully when no audio files are found.
        """
        # Simulate an empty directory
        mock_get_audio_files.return_value = []

        with patch("main.MongoClient"):
            with patch("main.transcribe_audio") as mock_transcribe:
                main()
                # Ensure transcription is not called
                mock_transcribe.assert_not_called()

    @patch("main.get_audio_files")
    @patch("main.transcribe_audio")
    @patch("main.analyze_sentiment")
    @patch("main.store_data")
    def test_pipeline_success(
        self, mock_store_data, mock_analyze_sentiment, mock_transcribe_audio, mock_get_audio_files
    ):
        """
        Test that the entire pipeline runs successfully for valid inputs.
        """
        # Mock dependencies
        mock_get_audio_files.return_value = ["test.wav"]
        mock_transcribe_audio.return_value = "mock transcript"
        mock_analyze_sentiment.return_value = {"mood": "Positive"}

        with patch("main.MongoClient"):
            main()

            # Verify each step in the pipeline is called as expected
            mock_transcribe_audio.assert_called_once_with("test.wav")
            mock_analyze_sentiment.assert_called_once_with("mock transcript")
            mock_store_data.assert_called_once()

    def test_setup_logging(self):
        """
        Test that logging is configured correctly.
        """
        with patch("logging.basicConfig") as mock_basic_config:
            setup_logging()
            mock_basic_config.assert_called_once_with(
                level=logging.DEBUG,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[unittest.mock.ANY],
            )


if __name__ == "__main__":
    unittest.main()
