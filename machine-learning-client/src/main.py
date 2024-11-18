"""
This module processes audio files, performs transcription and sentiment analysis,
and stores the results in a MongoDB database.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, session, flash, redirect, url_for, render_template
from flask_session import Session
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from utils import transcribe_audio, analyze_sentiment, store_data

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session encryption
app.config["SESSION_TYPE"] = "filesystem"  # Use filesystem-based session storage
Session(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "./processed_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/logout")
def logout():
    """
    Handle user logout.
    """
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if username is already taken
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another one.", "error")
            return redirect(url_for("register"))

        # Insert new user into the database
        new_user = {"username": username, "password": password}
        users_collection.insert_one(new_user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/process-audio", methods=["POST"])
@login_required
def process_audio():
    """
    Endpoint to process an uploaded audio file and store results in MongoDB.

    Returns:
        JSON: Processed results or error message.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    audio_file = request.files["audio"]
    user_id = request.form.get("user_id")
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)

    try:
        # Save the uploaded file locally
        audio_file.save(file_path)
        logger.info("Saved file: %s", file_path)

        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://root:secret@localhost:27017")
        client = MongoClient(mongo_uri)
        db = client["voice_mood_journal"]
        collection = db["entries"]
        users_collection = db["users"]

        # Perform transcription
        text = transcribe_audio(file_path)
        logger.debug("Transcription: %s", text)

        # Perform sentiment analysis
        sentiment = analyze_sentiment(text)
        logger.debug("Sentiment: %s", sentiment)

        # Prepare data for MongoDB
        data = {
            "user_id": user_id,
            "file_name": audio_file.filename,
            "transcript": text,
            "sentiment": sentiment,
            "timestamp": datetime.utcnow(),
        }

        # Store the data in MongoDB
        store_data(collection, data)
        logger.info("Successfully processed and stored data for %s", file_path)

        return jsonify({"status": "success", "data": data}), 200
    except IOError as io_error:
        logger.error("File handling error: %s", io_error)
        return jsonify({"error": "File handling failed", "details": str(io_error)}), 500

    except PyMongoError as mongo_error:
        logger.error("Database error: %s", mongo_error)
        return jsonify({"error": "Database error", "details": str(mongo_error)}), 500

    except RuntimeError as runtime_error:
        logger.error("Runtime error: %s", runtime_error)
        return jsonify({"error": "Runtime error", "details": str(runtime_error)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
