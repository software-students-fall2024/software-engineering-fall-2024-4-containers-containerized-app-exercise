"""
Flask application for processing audio files and saving transcripts to MongoDB.
"""

import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient, errors
from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv

load_dotenv()
# Ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set externally

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not found in environment variables.")

mongo_client = MongoClient(mongo_uri)
db = mongo_client["boyfriend_db"]
collection = db["speech_data"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

speech_client = speech.SpeechClient()  # Initialize the SpeechClient here


def convert_to_linear16(filepath):
    """Convert the audio file to LINEAR16 format."""
    output_path = filepath.replace(".wav", "_linear16.wav")
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # Overwrite output files without asking
            "-i",
            filepath,
            "-ar",
            "16000",
            "-ac",
            "1",
            "-sample_fmt",
            "s16",
            output_path,
        ],
        check=True,
    )
    return output_path


def transcribe_audio(filepath):
    """Transcribe audio using Google Speech-to-Text API."""
    try:
        with open(filepath, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        response = speech_client.recognize(config=config, audio=audio)
        if response.results:
            return response.results[0].alternatives[0].transcript
        return None
    except GoogleAPICallError as error:
        raise RuntimeError(f"Speech-to-Text API error: {error}") from error


def save_transcript_to_db(transcript):
    """Save the transcript to the MongoDB database."""
    try:
        result = collection.insert_one({"transcript": transcript})
        return str(result.inserted_id)
    except errors.PyMongoError as error:
        raise RuntimeError(f"MongoDB insertion failed: {error}") from error


@app.route("/")
def index():
    """Root endpoint to confirm the server is running."""
    return "Welcome to the audio processing server!"


@app.route("/process-audio", methods=["POST"])
def process_audio():
    """Process an audio file and save its transcript."""
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        converted_filepath = convert_to_linear16(filepath)
        transcript = transcribe_audio(converted_filepath)

        if transcript:
            document_id = save_transcript_to_db(transcript)
            return jsonify({"transcript": transcript, "id": document_id})
        return jsonify({"error": "No speech recognized"}), 400
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 500
    finally:
        cleanup_files([filepath, converted_filepath])


def cleanup_files(file_list):
    """Remove temporary files."""
    for temp_file in file_list:
        try:
            os.remove(temp_file)
        except OSError as error:
            print(f"Error removing file {temp_file}: {error}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
