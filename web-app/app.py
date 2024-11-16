"""
This is the web-app, running as a flask server.
"""

from os import getenv
from flask import Flask, jsonify, render_template, request
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
medata_collection = db["audio_metadata"]


@app.route("/")
def index():
    """
    Index route
    """
    return render_template("index.html")


@app.route("/record")
def register():
    """
    Record route
    """
    return render_template("record.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    """
    Endpoint to upload files and send to ml client
    """
    ml_client_url = "http://localhost:5050/predict"
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    try:
        response = requests.post(
            ml_client_url,
            files={
                "audio": (audio_file.filename, audio_file.stream, audio_file.mimetype)
            },
            timeout=10,
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return (
            jsonify({"error": "Failed to send audio to ML client", "details": str(e)}),
            500,
        )


if __name__ == "__main__":
    print("App listening on port 8080")
    app.run(host="0.0.0.0", port=8080, debug=True)
