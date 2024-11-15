"""
This module processes audio files, performs transcription and sentiment analysis,
and stores the results in a MongoDB database.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from utils import transcribe_audio, analyze_sentiment, store_data

load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "./processed_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/process-audio", methods=["POST"])
def process_audio():
    """
    Endpoint to process an uploaded audio file and store results in MongoDB.

    Returns:
        JSON: Processed results or error message.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)

    try:
        # Save the uploaded file locally
        audio_file.save(file_path)
        logger.info("Saved file: %s", file_path)

        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://root:voice_mood@localhost:27017")
        client = MongoClient(mongo_uri)
        db = client["voice_mood_journal"]
        collection = db["entries"]

        # Perform transcription
        text = transcribe_audio(file_path)
        logger.debug("Transcription: %s", text)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(text)
        logger.debug("Sentiment: %s", sentiment)

        # Prepare data for MongoDB
        data = {
            "file_name": audio_file.filename,
            "transcript": text,
            "sentiment": sentiment,
            "timestamp": datetime.utcnow(),
        }

        # Store the data in MongoDB
        store_data(collection, data)
        logger.info("Successfully processed and stored data for %s", file_path)

        return jsonify({"status": "success", "data": data}), 200

    except Exception as error:
        logger.error("Error processing file: %s", error)
        return jsonify({"error": "Processing failed", "details": str(error)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)

# def main():
#     """
#     Main function to run the audio processing and sentiment analysis pipeline.

#     This function loads environment variables, connects to the MongoDB database,
#     processes each audio file in the specified directory, transcribes it, performs
#     sentiment analysis, and stores the data in MongoDB. If no audio files are found,
#     it logs a warning message.
#     """
#     load_dotenv()
#     mongo_uri = os.getenv("MONGO_URI", "mongodb://root:voice_mood@localhost:27017")
#     audio_dir = os.getenv("AUDIO_DIR", "./audio")
#     setup_logging()
#     logger = logging.getLogger(__name__)
#     try:
#         client = MongoClient(mongo_uri)
#         db = client["voice_mood_journal"]
#         collection = db["entries"]
#         logger.info("Connected to MongoDB.")
#     except pymongo.errors.ConnectionFailure as e:
#         logger.error("Failed to connect to MongoDB: %s", e)
#         return

#     audio_files = get_audio_files(audio_dir)
#     # Retrieves audio files from the specified directory.

#     if not audio_files:

#         logger.warning("There are no audio files in the directory.")
#         return

#     for file_path in audio_files:
#         try:
#             logger.info("Processing file: %s", file_path)
#             text = transcribe_audio(file_path)
#             logger.debug("Transcription: %s", text)
#             sentiment = analyze_sentiment(text)
#             logger.debug("Sentiment: %s", sentiment)

#             data = {
#                 "file_name": os.path.basename(file_path),
#                 "transcript": text,
#                 "sentiment": sentiment,
#                 "timestamp": datetime.utcnow(),
#             }

#             store_data(collection, data)
#             logger.info("Successfully processed and stored data for %s", file_path)

#         except Exception as e:  # pylint: disable=broad-except
#             logger.error("Error processing %s: %s", file_path, e)

# if __name__ == "__main__":
#     main()
