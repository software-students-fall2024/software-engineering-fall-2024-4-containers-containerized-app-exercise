"""
Unit tests for Flask application and MongoDB operations in the boyfriend client.
"""

import os
import pytest
from bson.objectid import ObjectId
from gtts import gTTS

from app import (
    app,
    collection,
    convert_to_linear16,
    transcribe_audio,
    save_transcript_to_db,
)


@pytest.fixture(name="clear_test_data")
def clear_test_data_fixture():
    """Clean up test data before and after tests."""
    collection.delete_many({"transcript": {"$regex": "test.*"}})
    yield
    collection.delete_many({"transcript": {"$regex": "test.*"}})


@pytest.fixture(name="client")
def client_fixture():
    """Set up Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index(client):
    """Test the root endpoint of the Flask app."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the audio processing server!" in response.data


def test_mongodb_connection(clear_test_data):
    """Test MongoDB connection and basic insert and retrieve operations."""
    _ = clear_test_data  # Suppress unused-argument warning
    result = collection.insert_one({"transcript": "test transcript"})
    assert result.inserted_id is not None
    saved_doc = collection.find_one({"_id": result.inserted_id})
    assert saved_doc is not None
    assert saved_doc["transcript"] == "test transcript"


def test_convert_to_linear16():
    """Test audio conversion to LINEAR16 format."""
    input_file = "test_audio.wav"
    output_file = "test_audio_linear16.wav"
    os.system(f"ffmpeg -f lavfi -i sine=frequency=1000:duration=1 {input_file}")
    output_path = convert_to_linear16(input_file)
    assert os.path.exists(output_path)
    assert output_path == output_file
    os.remove(input_file)
    os.remove(output_path)


def test_transcribe_audio():
    """Test audio transcription with a dummy audio file."""
    input_file = "test_audio_linear16.wav"
    os.system(
        f"ffmpeg -f lavfi -i sine=frequency=1000:duration=1 "
        f"-ar 16000 -ac 1 -sample_fmt s16 {input_file}"
    )
    transcript = transcribe_audio(input_file)
    assert transcript is None
    os.remove(input_file)


def test_save_transcript_to_db(clear_test_data):
    """Test saving a transcript to MongoDB."""
    _ = clear_test_data
    transcript = "This is a test transcript."
    document_id = save_transcript_to_db(transcript)
    assert document_id is not None
    assert ObjectId.is_valid(document_id)
    saved_doc = collection.find_one({"_id": ObjectId(document_id)})
    assert saved_doc is not None
    assert saved_doc["transcript"] == transcript


def test_process_audio_endpoint(client, clear_test_data):
    """Test the /process-audio endpoint."""
    _ = clear_test_data
    input_file = "test_audio.wav"
    os.system(f"ffmpeg -f lavfi -i sine=frequency=1000:duration=1 {input_file}")
    with open(input_file, "rb") as audio:
        response = client.post("/process-audio", data={"audio": audio})
    assert response.status_code == 400
    assert b"No speech recognized" in response.data
    os.remove(input_file)


def test_real_transcription():
    """Test transcription with real speech audio."""
    input_text = "Hello, this is a test."
    input_file = "real_speech.wav"

    tts = gTTS(text=input_text, lang="en")
    tts.save(input_file)

    linear16_file = convert_to_linear16(input_file)

    transcript = transcribe_audio(linear16_file)
    assert transcript is not None
    assert "test" in transcript.lower()

    os.remove(input_file)
    os.remove(linear16_file)
