from unittest.mock import patch, MagicMock
from src.utils import get_audio_files, transcribe_audio, analyze_sentiment, store_data


@patch("src.utils.glob.glob", return_value=["file1.wav", "file2.wav"])
def test_get_audio_files(mock_glob):
    """
    Test the `get_audio_files` function to ensure it returns the correct audio files.
    """
    audio_files = get_audio_files("./mock_directory")
    assert len(audio_files) == 2
    assert "file1.wav" in audio_files
    mock_glob.assert_called_once_with("./mock_directory/*.wav")


@patch("src.utils.sr.Recognizer")
def test_transcribe_audio(mock_recognizer):
    """
    Test the `transcribe_audio` function to ensure it returns the correct transcription.
    """
    mock_instance = MagicMock()
    mock_recognizer.return_value = mock_instance
    mock_instance.record.return_value = "audio data"
    mock_instance.recognize_google.return_value = "Transcription success"

    with patch("src.utils.sr.AudioFile"):
        text = transcribe_audio("mock_file.wav")
        assert text == "Transcription success"
        mock_instance.recognize_google.assert_called_once()


@patch("src.utils.sr.Recognizer")
def test_transcribe_audio_error(mock_recognizer):
    """
    Test the `transcribe_audio` function when an error occurs during transcription.
    """
    mock_instance = MagicMock()
    mock_recognizer.return_value = mock_instance
    mock_instance.record.return_value = "audio data"
    mock_instance.recognize_google.side_effect = Exception("Mocked error")

    with patch("src.utils.sr.AudioFile"):
        result = transcribe_audio("mock_file.wav")

    # Ensure the function handles the exception gracefully and returns an empty string
    assert result == ""


def test_analyze_sentiment():
    """
    Test the `analyze_sentiment` function to ensure it returns correct sentiment analysis.
    """
    result = analyze_sentiment("I love coding")
    assert result["mood"] == "Positive"
    assert result["polarity"] > 0

    result = analyze_sentiment("I hate bugs")
    assert result["mood"] == "Negative"
    assert result["polarity"] < 0


@patch("src.utils.pymongo.MongoClient")
@patch("src.utils.pymongo.collection.Collection.insert_one")
def test_store_data(mock_insert_one, mock_mongo_client):
    """
    Test the `store_data` function to ensure data is inserted into MongoDB correctly.
    """
    # Mock the `insert_one` method
    mock_insert_one.return_value = None

    # Create test data
    mock_collection = MagicMock()
    data = {"key": "value"}

    # Call the function
    store_data(mock_collection, data)

    # Assert that `insert_one` was called with the correct data
    mock_insert_one.assert_called_once_with(data)
