"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""

from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import speech_recognition as sr
import os
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
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        # Validate file_id format
        file_id = ObjectId(file_id)
    except:
        return jsonify({"error": "Invalid file_id format"}), 400

    try:
        # Check if file exists in GridFS
        if not fs.exists(file_id):
            return jsonify({"error": "File not found"}), 404

        # Retrieve file from GridFS
        grid_file = fs.get(file_id)

        # Create a temporary file
        temp_path = f"temp_{file_id}.wav"
        try:
            # Write GridFS file to temporary file
            with open(temp_path, "wb") as f:
                f.write(grid_file.read())

            # Initialize recognizer and process audio
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Update metadata collection
            update_result = metadata.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "transcription": text,
                        "processed_time": datetime.utcnow(),
                        "status": "completed",
                    }
                },
            )

            if update_result.modified_count == 0:
                return jsonify({"error": "Failed to update metadata"}), 500

            return (
                jsonify(
                    {
                        "message": "Prediction completed successfully",
                        "file_id": str(file_id),
                        "status": "completed",
                        "transcription": text,
                    }
                ),
                200,
            )

        except sr.UnknownValueError:
            # Update metadata with error
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
            return (
                jsonify(
                    {
                        "message": "Speech recognition failed",
                        "file_id": str(file_id),
                        "status": "failed",
                        "error": "Speech could not be understood",
                    }
                ),
                400,
            )

        except Exception as e:
            # Update metadata with error
            metadata.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "processed_time": datetime.utcnow(),
                    }
                },
            )
            return (
                jsonify(
                    {
                        "message": "Processing failed",
                        "file_id": str(file_id),
                        "status": "failed",
                        "error": str(e),
                    }
                ),
                500,
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Server error",
                    "file_id": str(file_id),
                    "status": "error",
                    "error": str(e),
                }
            ),
            500,
        )


if __name__ == "__main__":
    print("ML Client running on port 5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
