import pytest
import mongomock
import numpy as np
import os
import wave
from datetime import datetime
from speech_to_text import analyze_noise, suppress_noise, save_to_db

# Mock MongoDB setup
@pytest.fixture
def mock_collection():
    mock_client = mongomock.MongoClient()
    return mock_client.audio_analysis.audio_logs

# Test analyze_noise function
def test_analyze_noise(tmp_path):
    audio_path = tmp_path / "test.wav"
    with wave.open(audio_path, "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(44100)
        wave_file.writeframes(np.array([100] * 44100, dtype=np.int16).tobytes())

    avg_amp, noise_level = analyze_noise(audio_file_path=str(audio_path), noise_threshold=50)
    
    assert avg_amp == 100
    assert noise_level == "High"

# Test suppress_noise function
def test_suppress_noise(tmp_path):

    input_audio_path = tmp_path / "input.wav"
    output_audio_path = tmp_path / "output.wav"
    
    data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    samplerate = 44100

    with wave.open(input_audio_path, "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(4)
        wave_file.setframerate(samplerate)
        wave_file.writeframes((data * (2**15 - 1)).astype(np.int16).tobytes())

    suppress_noise(str(input_audio_path), str(output_audio_path))

    assert os.path.exists(output_audio_path)

    with wave.open(output_audio_path, "rb") as wave_file:
        reduced_data = np.frombuffer(wave_file.readframes(-1), dtype=np.int16)
        assert not np.allclose(data, reduced_data)

# Test save_to_db function
def test_save_to_db(mock_collection):
    audio_file_path = "test_audio.wav"
    reduced_file_path = "test_audio_reduced.wav"
    avg_amp = 25.5
    noise_level = "Low"
    transcription = "This is a test transcription."

    save_to_db(audio_file_path, reduced_file_path, avg_amp, noise_level, transcription)

    inserted_docs = list(mock_collection.find())
    assert len(inserted_docs) == 1
    doc = inserted_docs[0]
    assert doc["original_file"] == audio_file_path
    assert doc["processed_file"] == reduced_file_path
    assert doc["average_amplitude"] == avg_amp
    assert doc["noise_level"] == noise_level
    assert doc["transcription"] == transcription
    assert isinstance(doc["timestamp"], datetime)