"""
This module represents the entry point source file for ml-client.
"""

import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
import speech_recognition as sr

app = Flask(__name__)
# Connect to MangoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.database
collections = db.transcriptions


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """function to transcribe the audio to text

    Returns:
        JSON: the object with transcribed text there
    """
    if "audio" not in request.files:
        return jsonify({"status": "fail", "text": "No audio file provided"})

    # Get the audio file from the request
    audio_file = request.files["audio"]
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        # Use the recognizer to transcribe the audio
        text = recognizer.recognize_google(audio_data)
        transcription_entry = {"transcription": text}
        result = collections.insert_one(transcription_entry)
        return jsonify({"status": "success", "id": str(result.inserted_id)})
    except sr.UnknownValueError:
        return jsonify({"status": "fail", "text": "Could not understand audio"})
    except sr.RequestError as e:
        return jsonify(
            {
                "status": "fail",
                "text": f"Could not request results from Google Speech Recognition service {e}",
            }
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
