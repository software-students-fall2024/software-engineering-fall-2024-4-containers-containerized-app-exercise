"""
Unit tests for the Machine Learning Client.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pymongo.errors import PyMongoError
from google.api_core.exceptions import GoogleAPICallError
from machine_learning_client import (
    convert_to_linear16,
    transcribe_audio,
    save_transcript_to_db,
    process_file,
    cleanup_files,
    AudioFileHandler,
    UPLOAD_FOLDER,
    collection,
)


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Fixture to set up and tear down the environment."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    yield
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            os.remove(os.path.join(UPLOAD_FOLDER, file))


def test_convert_to_linear16():
    """Test audio file conversion to LINEAR16 format."""
    input_file = os.path.join(UPLOAD_FOLDER, "test_audio.wav")
    output_file = os.path.join(UPLOAD_FOLDER, "test_audio_linear16.wav")

    # Create a dummy sine wave audio file
    os.system(f"ffmpeg -f lavfi -i sine=frequency=1000:duration=1 {input_file}")
    converted_path = convert_to_linear16(input_file)

    # Check the output file
    assert os.path.exists(converted_path)
    assert converted_path == output_file

    # Cleanup
    os.remove(input_file)
    os.remove(converted_path)


@patch("machine_learning_client.speech_client.recognize")
def test_transcribe_audio(mock_recognize):
    """Test audio transcription using Google Speech-to-Text."""
    input_file = os.path.join(UPLOAD_FOLDER, "test_audio_linear16.wav")

    # Create a dummy sine wave audio file
    os.system(
        f"ffmpeg -f lavfi -i sine=frequency=1000:duration=1 -ar 16000 -ac 1 -sample_fmt s16 {input_file}"
    )

    # Mock the transcription response
    mock_recognize.return_value.results = [
        MagicMock(alternatives=[MagicMock(transcript="This is a test transcript")])
    ]

    transcript = transcribe_audio(input_file)
    assert transcript == "This is a test transcript"

    # Cleanup
    os.remove(input_file)


@patch("machine_learning_client.collection.insert_one")
def test_save_transcript_to_db(mock_insert_one):
    """Test saving transcription to MongoDB."""
    mock_insert_one.return_value.inserted_id = "mocked_id"
    transcript = "This is a test transcript."

    doc_id = save_transcript_to_db(transcript)

    assert doc_id == "mocked_id"
    mock_insert_one.assert_called_once_with({"transcript": transcript})


def test_cleanup_files():
    """Test cleanup of temporary files."""
    test_file = os.path.join(UPLOAD_FOLDER, "temp_file.wav")
    with open(test_file, "w") as f:
        f.write("Temporary data.")

    assert os.path.exists(test_file)
    cleanup_files(test_file)
    assert not os.path.exists(test_file)


@patch("machine_learning_client.process_file")
def test_audio_file_handler(mock_process_file):
    """Test the AudioFileHandler for detecting new and modified files."""
    handler = AudioFileHandler()
    test_file = os.path.join(UPLOAD_FOLDER, "new_audio.wav")

    # Simulate file creation
    handler.on_created(type("Event", (object,), {"src_path": test_file, "is_directory": False}))
    mock_process_file.assert_called_once_with(test_file)

    # Simulate file modification
    handler.on_modified(type("Event", (object,), {"src_path": test_file, "is_directory": False}))
    mock_process_file.assert_called_with(test_file)


@patch("machine_learning_client.convert_to_linear16", side_effect=RuntimeError("Conversion error"))
def test_process_file_conversion_error(mock_convert_to_linear16):
    """Test process_file handling conversion errors."""
    test_file = os.path.join(UPLOAD_FOLDER, "error_audio.wav")
    with pytest.raises(RuntimeError, match="Conversion error"):
        process_file(test_file)


@patch("machine_learning_client.transcribe_audio", side_effect=GoogleAPICallError("API error"))
def test_process_file_transcription_error(mock_transcribe_audio):
    """Test process_file handling transcription errors."""
    test_file = os.path.join(UPLOAD_FOLDER, "error_audio.wav")
    with pytest.raises(RuntimeError, match="API error"):
        process_file(test_file)


@patch("machine_learning_client.save_transcript_to_db", side_effect=PyMongoError("DB error"))
def test_process_file_db_error(mock_save_transcript_to_db):
    """Test process_file handling database errors."""
    test_file = os.path.join(UPLOAD_FOLDER, "error_audio.wav")
    with pytest.raises(RuntimeError, match="DB error"):
        process_file(test_file)
