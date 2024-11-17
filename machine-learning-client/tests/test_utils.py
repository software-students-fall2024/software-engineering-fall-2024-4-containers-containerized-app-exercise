"""
Unit tests for utils.py.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.utils import get_audio_files, transcribe_audio, analyze_sentiment, store_data
from pymongo.errors import PyMongoError


class TestUtils(unittest.TestCase):
    """Unit tests for the utils.py module."""

    @patch("src.utils.glob.glob")
    def test_get_audio_files(self, mock_glob):
        """Test that get_audio_files retrieves the correct list of audio files."""
        mock_glob.return_value = ["audio1.wav", "audio2.wav"]
        audio_files = get_audio_files("./test_audio")
        self.assertEqual(audio_files, ["audio1.wav", "audio2.wav"])
        mock_glob.assert_called_once_with(os.path.join("./test_audio", "*.wav"))

    @patch("src.utils.sr.AudioFile")
    @patch("src.utils.sr.Recognizer")
    def test_transcribe_audio_success(self, mock_recognizer, mock_audio_file):
        """Test that transcribe_audio correctly transcribes audio files."""
        mock_instance = MagicMock()
        mock_instance.recognize_google.return_value = "Hello world"
        mock_recognizer.return_value = mock_instance

        with patch("builtins.open", mock_open()):
            transcription = transcribe_audio("test.wav")
            self.assertEqual(transcription, "Hello world")
            mock_instance.recognize_google.assert_called_once()

    @patch("src.utils.sr.AudioFile")
    @patch("src.utils.sr.Recognizer")
    def test_transcribe_audio_failure(self, mock_recognizer, mock_audio_file):
        """Test that transcribe_audio handles errors gracefully."""
        mock_instance = MagicMock()
        mock_instance.recognize_google.side_effect = Exception("Speech not recognized")
        mock_recognizer.return_value = mock_instance

        with patch("builtins.open", mock_open()):
            transcription = transcribe_audio("test.wav")
            self.assertEqual(transcription, "")
            mock_instance.recognize_google.assert_called_once()

    def test_analyze_sentiment_positive(self):
        """Test analyze_sentiment for positive polarity text."""
        result = analyze_sentiment("I love programming!")
        self.assertEqual(result["mood"], "Positive")
        self.assertGreater(result["polarity"], 0)

    def test_analyze_sentiment_negative(self):
        """Test analyze_sentiment for negative polarity text."""
        result = analyze_sentiment("I hate bugs!")
        self.assertEqual(result["mood"], "Negative")
        self.assertLess(result["polarity"], 0)

    def test_analyze_sentiment_neutral(self):
        """Test analyze_sentiment for neutral text."""
        result = analyze_sentiment("This is a sentence.")
        self.assertEqual(result["mood"], "Neutral")
        self.assertEqual(result["polarity"], 0)

    @patch("src.utils.logging.info")
    @patch("src.utils.logging.error")
    @patch("src.utils.pymongo.collection.Collection.insert_one")
    def test_store_data_success(self, mock_insert_one, mock_logging_error, mock_logging_info):
        """Test that store_data successfully stores data in MongoDB."""
        mock_collection = MagicMock()
        data = {"key": "value"}
        store_data(mock_collection, data)
        mock_insert_one.assert_called_once_with(data)
        mock_logging_info.assert_called_once_with("Data stored successfully.")
        mock_logging_error.assert_not_called()

    @patch("src.utils.logging.error")
    @patch("src.utils.pymongo.collection.Collection.insert_one")
    def test_store_data_failure(self, mock_insert_one, mock_logging_error):
        """Test that store_data handles MongoDB errors gracefully."""
        mock_insert_one.side_effect = PyMongoError("Insertion failed")
        mock_collection = MagicMock()
        data = {"key": "value"}
        store_data(mock_collection, data)
        mock_logging_error.assert_called_once_with("Failed to store data: %s", "Insertion failed")


if __name__ == "__main__":
    unittest.main()
