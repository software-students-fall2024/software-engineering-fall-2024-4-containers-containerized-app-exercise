"""
This is the Flask web application that serves as the interface for
the machine learning model.
"""

import io
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from pydub import AudioSegment
from bson import ObjectId
import requests

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.database
collections = db.transcriptions


def create_app():
    """
    Create and configure the Flask application
    Returns: app: the Falsk application object
    """
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/record", methods=["POST"])
    def record():
        audio_data = request.files["audio"]
        if audio_data:
            try:
                audio = AudioSegment.from_file(audio_data)
                audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
                buffer = io.BytesIO()
                audio.export(buffer, format="wav")
                buffer.seek(0)
                response = requests.post(
                    "http://ml-client:5000/transcribe",
                    files={"audio": ("audio.wav", buffer, "audio/wav")},
                    timeout=10,
                )
                data = response.json()
                if data.get("status") == "success":
                    data_id = ObjectId(data.get("id"))
                    text = collections.find_one({"_id": data_id}).get("transcription")
                    return jsonify({"status": "success", "text": text})
            except ValueError:
                return jsonify({"status": "error", "text": "ValueError happens"})
        return jsonify({"status": "error", "text": response.json().get("text")})

    return app


if __name__ == "__main__":
    web_app = create_app()
    web_app.run(host="0.0.0.0")
