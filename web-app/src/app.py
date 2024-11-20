"""
This is the web-app portion
"""

from datetime import datetime
from os import getenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from gridfs import GridFS
import requests

connstr = getenv("DB_URI")
key = getenv("SECRET")

if connstr is None:
    raise ValueError("Database URI could not be loaded: check .env file")

if key is None:
    raise ValueError("Flask secret could not be loaded: check .env file")

app = Flask(__name__)
app.secret_key = key

client = MongoClient(connstr)
db = client["audio_db"]
grid_fs = GridFS(db)
metadata_collection = db["audio_metadata"]


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    """
    Endpoint to upload files and store raw binary in GridFS with metadata.
    Notifies the ML client upon successful storage.
    """
    if "audio" not in request.files or "name" not in request.form:
        return jsonify({"error": "Audio file and name are required"}), 400

    audio_file = request.files["audio"]
    file_name = request.form["name"]

    ml_client_url = "http://machine-learning-client:5050/predict"

    # Store raw binary file in GridFS with metadata
    print("MIME TYPE: ", audio_file.mimetype)
    gridfs_id = grid_fs.put(
        audio_file,
        filename=file_name,
        content_type=audio_file.mimetype,  # Store the MIME type
    )

    if not gridfs_id:
        return jsonify({"error": "Failed to store the audio file in GridFS"}), 500

    # Store metadata in metadata collection
    metadata = {
        "file_id": str(gridfs_id),
        "name": file_name,
        "upload_time": datetime.utcnow(),
        "transcription": "",
    }

    metadata_result = metadata_collection.insert_one(metadata)

    if not metadata_result.acknowledged:
        return jsonify({"error": "Failed to store the metadata in the database"}), 500

    print("File successfully uploaded with GridFS ID:", gridfs_id)

    # Notify ML client
    try:
        response = requests.get(
            ml_client_url,
            params={"file_id": str(gridfs_id)},
            timeout=10,
        )

        if response.status_code == 200:
            return (
                jsonify(
                    {
                        "message": "File uploaded successfully, and ML client notified.",
                        "file_id": str(gridfs_id),
                    }
                ),
                200,
            )
        return (
            jsonify(
                {
                    "message": "File uploaded, but ML client responded with an error.",
                    "file_id": str(gridfs_id),
                    "ml_client_response": response.text,
                }
            ),
            500,
        )

    except requests.exceptions.RequestException as e:
        return (
            jsonify(
                {
                    "message": "File uploaded, but failed to notify ML client.",
                    "file_id": str(gridfs_id),
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/")
def index():
    """
    Index route
    """

    # Fetch metadata
    metadata = list(
        metadata_collection.find(
            {},
            {"file_id": 1, "name": 1, "upload_time": 1, "transcription": 1, "_id": 0},
        )
    )
    print(metadata)

    return render_template("index.html", recordings=metadata)


@app.route("/record")
def record():
    """
    Record route
    """
    return render_template("record.html")


if __name__ == "__main__":
    print("App listening on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
