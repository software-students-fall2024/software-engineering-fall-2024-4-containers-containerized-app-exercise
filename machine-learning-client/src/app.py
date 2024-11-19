"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request
from pymongo import MongoClient, errors as mongo_errors
from bson import ObjectId, errors as bson_errors
import speech_recognition as sr
import gridfs

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.environ["MONGODB_URI"])
db = client["transcription_db"]

# Collections
fs = gridfs.GridFS(db)  # For file storage
metadata = db["metadata"]  # For metadata storage


@app.route("/")
def home():
    """
    Home route that returns a greeting message.

    Returns:
        str: A simple greeting message.
    """
    return "<h1>ML Client Service</h1>"


@app.route("/predict")
def predict():
    """
    Handles the prediction based on file_id.
    Retrieves audio file from GridFS, performs speech-to-text,
    and updates metadata collection with results.

    Returns:
        tuple: JSON response and status code
    """
    file_id = request.args.get("file_id")
    response = {}
    status_code = 200  # Default to 200 OK

    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    temp_path = None  # Initialize temp_path to ensure cleanup in finally block
    try:
        # Validate file_id format
        file_id = ObjectId(file_id)

        # Check if file exists in GridFS
        if not fs.exists(file_id):
            return jsonify({"error": "File not found"}), 404

        # Retrieve file from GridFS
        grid_file = fs.get(file_id)
        temp_path = f"temp_{file_id}.wav"
        with open(temp_path, "wb") as f:
            f.write(grid_file.read())

        # Perform speech-to-text
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)

        # Update metadata with transcription
        update_result = metadata.update_one(
            {"file_id": file_id},
            {
                "$set": {
                    "transcription": transcription,
                    "processed_time": datetime.utcnow(),
                    "status": "completed",
                }
            },
        )
        if update_result.modified_count == 0:
            response = {"error": "Failed to update metadata"}
            status_code = 500
        else:
            response = {
                "message": "Prediction completed successfully",
                "file_id": str(file_id),
                "status": "completed",
                "transcription": transcription,
            }

    except bson_errors.InvalidId:
        response = {"error": "Invalid file_id format"}
        status_code = 400

    except sr.UnknownValueError:
        # Handle speech recognition failure
        metadata.update_one(
            {"file_id": file_id},
            {
                "$set": {
                    "status": "failed",
                    "error": "Speech could not be understood",
                    "processed_time": datetime.utcnow(),
                }
            },
        )
        response = {
            "message": "Speech recognition failed",
            "file_id": str(file_id),
            "status": "failed",
            "error": "Speech could not be understood",
        }
        status_code = 400

    except sr.RequestError as api_error:
        # Handle API connection errors
        metadata.update_one(
            {"file_id": file_id},
            {
                "$set": {
                    "status": "failed",
                    "error": f"Speech recognition API error: {str(api_error)}",
                    "processed_time": datetime.utcnow(),
                }
            },
        )
        response = {
            "message": "Speech recognition API error",
            "file_id": str(file_id),
            "status": "failed",
            "error": str(api_error),
        }
        status_code = 500

    except mongo_errors.PyMongoError as db_error:
        # Handle database errors
        response = {
            "message": "Database error occurred",
            "file_id": str(file_id),
            "status": "error",
            "error": str(db_error),
        }
        status_code = 500

    finally:
        # Ensure cleanup of temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify(response), status_code


if __name__ == "__main__":
    print("ML Client running on port 5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
