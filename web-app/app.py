"""
This is the web-app
"""

from datetime import datetime
from os import getenv
from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
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
audio_collection = db["audio_files"]
metadata_collection = db["audio_metadata"]


@app.route("/")
def index():
    """
    Index route
    """

    # Fetch metadata
    metadata = list(
        metadata_collection.find({}, {"file_id": 1, "name": 1, "upload_time": 1, "transcription": 1, "_id": 0})
    )

    return render_template("index.html", recordings=metadata)


@app.route("/record")
def record():
    """
    Record route
    """
    return render_template("record.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    """
    Endpoint to upload files and send to ml client
    """
    ml_client_url = "http://machine-learning-client:5050/predict"

    if "audio" not in request.files or "name" not in request.form:
        return jsonify({"error": "Audio file and name are required"}), 400

    audio_file = request.files["audio"]
    file_name = request.form["name"]

    file_id = audio_collection.insert_one(
        {
            "file_name": file_name,
            "file_data": audio_file.read(),
            "content_type": audio_file.mimetype,
        }
    ).inserted_id
    if not file_id:
        return jsonify({"error": "Failed to store the audio file in the database"}), 500

    metadata = {
        "file_id": file_id,
        "name": file_name,
        "upload_time": datetime.utcnow(),
        "transcription": "",
    }

    metadata_result = metadata_collection.insert_one(metadata)

    if not metadata_result.acknowledged:
        return jsonify({"error": "Failed to store the metadata in the database"}), 500

    print("File successfully uploaded with file_id", file_id)
    try:
        response = requests.get(
            ml_client_url,
            params={"file_id": file_id},
            timeout=10,
        )

        if not response.ok:
            return (
                jsonify(
                    {
                        "error": "ML client responded with an error",
                        "details": response.text,
                    }
                ),
                response.status_code,
            )

        return redirect(url_for("index"))

    except requests.exceptions.RequestException as e:
        # Handle exceptions during the request
        return (
            jsonify({"error": "Failed to notify ML client", "details": str(e)}),
            500,
        )


if __name__ == "__main__":
    print("App listening on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
