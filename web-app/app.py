"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""

import os  # Standard library imports
import subprocess
import uuid
from datetime import datetime
import logging
import requests
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from uuid import uuid4


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
ML_CLIENT_URL = os.getenv(
    "ML_CLIENT_URL", "http://machine-learning-client:5001/process-audio"
)

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client["voice_mood_journal"]
collection = db["entries"]

# Directory to temporarily store uploaded files
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    """Render the homepage with mood summary data."""
    mood_entries = collection.find().sort("timestamp", -1).limit(100)
    entries = [
        {
            "file_name": entry["file_name"],
            "transcript": entry["transcript"],
            "sentiment": entry["sentiment"],
            "timestamp": entry["timestamp"],
        }
        for entry in mood_entries
    ]

    return render_template("index.html", entries=entries)


def convert_to_pcm_wav(input_file, output_file):
    """
    Convert an audio file to PCM WAV format using ffmpeg.

    Args:
        input_file (str): Path to the input audio file.
        output_file (str): Path to save the converted WAV file.

    Raises:
        RuntimeError: If ffmpeg fails to convert the file.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}") from e


@app.route("/upload", methods=["POST"])
def upload_audio():
    """
    Handle audio file uploads from the frontend.
    Saves the file locally and forwards it to the machine learning client.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Generate unique filenames
    file_extension = os.path.splitext(audio_file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    converted_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"converted_{unique_filename}"
    )

    try:
        audio_file.save(file_path)
    except IOError as io_error:
        return jsonify({"error": "Failed to save file", "details": str(io_error)}), 500

    try:
        # Convert the uploaded file to PCM WAV format
        convert_to_pcm_wav(file_path, converted_file_path)
    except RuntimeError as conversion_error:
        return (
            jsonify(
                {
                    "error": "Failed to convert file to PCM WAV",
                    "details": str(conversion_error),
                }
            ),
            500,
        )

    # Forward the **converted** file to the machine learning client
    try:
        with open(converted_file_path, "rb") as file_obj:
            response = requests.post(
                ML_CLIENT_URL, files={"audio": file_obj}, timeout=10
            )

        if response.status_code == 200:

            return (
                jsonify(
                    {
                        "message": "File uploaded and processed successfully",
                        "data": response.json(),
                    }
                ),
                200,
            )

        return (
            jsonify({"error": "ML client failed", "details": response.json()}),
            response.status_code,
        )

    except requests.exceptions.RequestException as req_error:
        return (
            jsonify(
                {
                    "error": "Failed to forward file to ML client",
                    "details": str(req_error),
                }
            ),
            500,
        )


@app.route("/show_results")
def show_results():
    """Render the results page."""
    return render_template("showResults.html")


@app.route("/api/mood-trends")
def mood_trends():
    """Provide mood trend data for visualization."""
    mood_counts = {
        "Positive": collection.count_documents({"sentiment.mood": "Positive"}),
        "Negative": collection.count_documents({"sentiment.mood": "Negative"}),
        "Neutral": collection.count_documents({"sentiment.mood": "Neutral"}),
    }
    return jsonify(mood_counts)


@app.route("/api/recent-entries")
def recent_entries():
    """Provide recent entries data."""
    try:
        entries = collection.find().sort("timestamp", -1).limit(100)
        entries_list = [
            {
                "file_name": entry.get("file_name", ""),
                "transcript": entry.get("transcript", ""),
                "sentiment": entry.get("sentiment", ""),
                "timestamp": (
                    entry.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(entry.get("timestamp"), datetime)
                    else entry.get("timestamp", "")
                ),
            }
            for entry in entries
        ]
        return jsonify(entries_list), 200
    except PyMongoError as mongo_error:
        # Log the error
        logging.error("Database error: %s", mongo_error)
        return jsonify({"error": "Database error occurred"}), 500

    except (TypeError, KeyError) as data_error:
        # Log the error
        logging.error("Data processing error: %s", data_error)
        return jsonify({"error": "Data processing error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
