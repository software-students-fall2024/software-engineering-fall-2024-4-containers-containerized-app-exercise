"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""


from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import io
import gridfs

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.environ['MONGODB_URI'])
db = client['transcription_db']

# Collections
fs = gridfs.GridFS(db)  # For file storage
metadata = db['metadata']  # For metadata storage


@app.route('/api/process', methods=['POST'])
def process_audio():
    try:
        # Get file_id from request
        data = request.get_json()
        if not data or 'file_id' not in data:
            return jsonify({"error": "No file_id provided"}), 400

        file_id = data['file_id']

        # Validate file_id format
        try:
            file_id = ObjectId(file_id)
        except:
            return jsonify({"error": "Invalid file_id format"}), 400

        # Retrieve file from GridFS
        if not fs.exists(file_id):
            return jsonify({"error": "File not found"}), 404

        grid_file = fs.get(file_id)

        # Create a temporary file to store the audio
        temp_path = f"temp_{file_id}.wav"
        try:
            # Write GridFS file to temporary file
            with open(temp_path, 'wb') as f:
                f.write(grid_file.read())

            # Initialize recognizer
            recognizer = sr.Recognizer()

            # Process the audio file
            with sr.AudioFile(temp_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

            # Update metadata collection with transcription
            update_result = metadata.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "transcription": text,
                        "processed_time": datetime.utcnow(),
                        "status": "completed"
                    }
                }
            )

            if update_result.modified_count == 0:
                return jsonify({"error": "Failed to update metadata"}), 500

            return jsonify({
                "success": True,
                "file_id": str(file_id),
                "transcription": text
            })

        except sr.UnknownValueError:
            # Update metadata with error
            metadata.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": "Speech could not be understood",
                        "processed_time": datetime.utcnow()
                    }
                }
            )
            return jsonify({"error": "Speech could not be understood"}), 400

        except Exception as e:
            # Update metadata with error
            metadata.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "processed_time": datetime.utcnow()
                    }
                }
            )
            return jsonify({"error": str(e)}), 500

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
