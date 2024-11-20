from flask import Flask, jsonify, request
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from datetime import datetime
from pydub import AudioSegment
from io import BytesIO
import speech_recognition as sr
import os

app = Flask(__name__)

# MongoDB setup
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["audio_db"]
fs = GridFS(db)
metadata = db["audio_metadata"]


def fetch_and_convert_to_wav(file_id):
    """
    Fetch binary audio from GridFS and convert it to WAV format.
    """
    # Retrieve the file from GridFS
    grid_file = fs.get(file_id)
    content_type = grid_file.content_type  # MIME type of the original file
    print(content_type)

    # Convert to WAV using pydub
    file_data = grid_file.read()
    audio = AudioSegment.from_file(BytesIO(file_data), format=content_type.split("/")[-1])
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    return wav_io


def perform_speech_recognition(wav_io):
    """
    Perform speech-to-text on a WAV file.
    """
    recognizer = sr.Recognizer()

    print(f"Buffer size: {len(wav_io.getvalue())} bytes")
    try:
        print("Starting speech recognition...")

        # Open the audio file from the in-memory buffer
        with sr.AudioFile(wav_io) as source:
            print("Audio file opened successfully.")
            
            # Record the audio
            audio_data = recognizer.record(source)
            print("Audio data recorded successfully.")
            
            # Perform speech-to-text
            transcription = recognizer.recognize_sphinx(audio_data)
            print("Transcription completed successfully:", transcription)
            
            return transcription

    except sr.UnknownValueError:
        print("CMU Sphinx could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"CMU Sphinx request failed: {e}")
        return None
    except Exception as e:
        print("Error during speech recognition:")
        print(str(e))
        raise


@app.route("/predict", methods=["GET"])
def predict():
    """
    Predict transcription for the given file_id.
    """
    file_id = request.args.get("file_id")
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        file_id = ObjectId(file_id)
        print("trying to fetch file")
        wav_io = fetch_and_convert_to_wav(file_id)
        print("file loaded and converted")
        transcription = perform_speech_recognition(wav_io)
        print("Transcription loaded:", transcription)

        result = metadata.update_one(
            {"file_id": str(file_id)},
            {
                "$set": {
                    "transcription": transcription,
                    "processed_time": datetime.utcnow(),
                    "status": "completed",
                }
            },
        )

        if result.matched_count == 0:
            print("No document matched the query. Update failed.")
        elif result.modified_count == 0:
            print("Document matched, but no changes were made.")
        else:
            print("Document updated successfully.")

        return jsonify({
            "message": "Prediction completed successfully",
            "file_id": str(file_id),
            "status": "completed",
            "transcription": transcription,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
