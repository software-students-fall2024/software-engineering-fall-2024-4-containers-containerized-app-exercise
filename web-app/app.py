"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""

import os  # Standard library imports
import requests

# from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv


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


@app.route("/upload", methods=["POST"])
def upload_audio():
    """
    Handle audio file uploads from the frontend.
    Saves the file locally and forwards it to the machine learning client.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # Save the uploaded file locally
    audio_file = request.files["audio"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)

    try:
        audio_file.save(file_path)
    except IOError as io_error:
        return jsonify({"error": "Failed to save file", "details": str(io_error)}), 500

    # Forward the file to the machine learning client
    try:
        with open(file_path, "rb") as file_obj:
            response = requests.post(
                ML_CLIENT_URL, files={"audio": file_obj}, timeout=60
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


@app.route("/api/mood-trends")
def mood_trends():
    """Provide mood trend data for visualization."""
    mood_counts = {
        "Positive": collection.count_documents({"sentiment.mood": "Positive"}),
        "Negative": collection.count_documents({"sentiment.mood": "Negative"}),
        "Neutral": collection.count_documents({"sentiment.mood": "Neutral"}),
    }
    return jsonify(mood_counts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
