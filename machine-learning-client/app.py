"""
This module represents the entry point source file for ml-client.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import speech_recognition as sr

app = Flask(__name__)
# Enable CORS for your web-app origin
CORS(app, origins="http://127.0.0.1:5001")
# Connect to MangoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.database
collections = db.transcriptions
print("before the function go")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """function to transcribe the audio to text

    Returns:
        JSON: the object with transcribed text there
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    # Get the audio file from the request
    audio_file = request.files["audio"]
    print("Received audio file:", request.files["audio"].filename)

    # Use SpeechRecogniction to convert audio to text
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        # Use the recognizer to transcribe the audio
        text = recognizer.recognize_google(audio_data)
        # Store the transcription in MongoDB
        transcription_entry = {"transcription": text}
        result = collections.insert_one(transcription_entry)
        return jsonify({"transcription": text, "id": str(result.inserted_id)})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        return (
            jsonify(
                {
                    "error": (
                        f"Could not request results from Google Speech Recognition service; "
                        f"{e}"
                    )
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
