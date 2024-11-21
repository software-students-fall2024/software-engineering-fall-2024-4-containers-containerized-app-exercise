import os
import subprocess
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient, errors
from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger("pymongo").setLevel(logging.WARNING)

# Ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set externally

# Flask app setup
app = Flask(__name__)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not found in environment variables.")

try:
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client["hellokittyai_db"]  
    collection = db["speech_data"]
    mongo_client.admin.command("ping")
    logging.info("Successfully connected to MongoDB!")
except errors.PyMongoError as error:
    logging.error(f"Failed to connect to MongoDB: {error}")
    raise

# Directory for uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Google Speech-to-Text client
try:
    speech_client = speech.SpeechClient()
    logging.info("Google Speech-to-Text client initialized.")
except Exception as e:
    logging.error(f"Failed to initialize Speech-to-Text client: {e}")
    raise


def convert_to_linear16(filepath):
    """Convert the audio file to LINEAR16 format."""
    logging.debug(f"Converting {filepath} to LINEAR16 format...")
    output_path = filepath.replace(".wav", "_linear16.wav")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",  # Overwrite output files without asking
                "-i",
                filepath,
                "-ar",
                "16000",
                "-ac",
                "1",
                "-sample_fmt",
                "s16",
                output_path,
            ],
            check=True,
        )
        logging.debug(f"Conversion successful: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg conversion failed for {filepath}: {e}")
        raise RuntimeError(f"FFmpeg conversion failed: {e}")


def transcribe_audio(filepath):
    """Transcribe audio using Google Speech-to-Text API."""
    logging.debug(f"Transcribing audio: {filepath}")
    try:
        with open(filepath, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )

        response = speech_client.recognize(config=config, audio=audio)
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            logging.debug(f"Transcription successful: {transcript}")
            return transcript
        logging.warning(f"No speech recognized in audio: {filepath}")
        return None
    except GoogleAPICallError as error:
        logging.error(f"Speech-to-Text API error for {filepath}: {error}")
        raise RuntimeError(f"Speech-to-Text API error: {error}")


def save_transcript_to_db(transcript):
    """Save the transcript to the MongoDB database."""
    logging.debug(f"Saving transcript to MongoDB: {transcript}")
    try:
        result = collection.insert_one({"transcript": transcript})
        logging.info(f"Transcript saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except errors.PyMongoError as error:
        logging.error(f"MongoDB insertion failed: {error}")
        raise RuntimeError(f"MongoDB insertion failed: {error}")


def process_file(filepath):
    """Process a single audio file."""
    logging.info(f"Processing file: {filepath}")
    try:
        converted_filepath = convert_to_linear16(filepath)
        transcript = transcribe_audio(converted_filepath)

        if transcript:
            document_id = save_transcript_to_db(transcript)
            logging.info(f"File processed and saved. Transcript ID: {document_id}")
        else:
            logging.warning(f"No speech recognized in file: {filepath}")
    except RuntimeError as error:
        logging.error(f"Error processing file {filepath}: {error}")
    finally:
        cleanup_files([filepath, converted_filepath])


def cleanup_files(file_list):
    """Remove temporary files."""
    for temp_file in file_list:
        try:
            os.remove(temp_file)
            logging.debug(f"Removed temporary file: {temp_file}")
        except OSError as error:
            logging.error(f"Error removing file {temp_file}: {error}")


class AudioFileHandler(FileSystemEventHandler):
    """Handles new files in the uploads folder."""

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".wav"):
            logging.info(f"New file detected: {event.src_path}")
            process_file(event.src_path)


# Flask endpoint for testing
@app.route("/")
def index():
    """Root endpoint to confirm the server is running."""
    return "Welcome to the audio processing server!"


if __name__ == "__main__":
    # Start monitoring the uploads folder
    observer = Observer()
    event_handler = AudioFileHandler()
    observer.schedule(event_handler, UPLOAD_FOLDER, recursive=False)
    observer.start()

    try:
        logging.info("Machine-learning-client is monitoring the uploads folder...")
        app.run(host="0.0.0.0", port=5001)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
