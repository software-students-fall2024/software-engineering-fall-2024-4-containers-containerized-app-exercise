"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""

import os  # Standard library imports
import subprocess
import uuid
from datetime import datetime
import logging
import requests
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from bson.objectid import ObjectId


# User Class
class User(UserMixin):
    """
    User class that extends UserMixin for Flask-Login.

    Attributes:
        id (str): The user's unique ID.
        username (str): The user's username.
        password (str): The user's hashed password.
    """

    def __init__(self, user_id, username, password):
        """
        Initialize the User object.

        Args:
            user_id (str): The user's unique ID.
            username (str): The user's username.
            password (str): The user's hashed password.
        """
        self.id = user_id
        self.username = username
        self.password = password


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
ML_CLIENT_URL = os.getenv(
    "ML_CLIENT_URL", "http://machine-learning-client:5001/process-audio"
)

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

client = MongoClient(MONGO_URI)
db = client["voice_mood_journal"]
collection = db["entries"]

# Directory to temporarily store uploaded files
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

##########################################
# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.

    Args:
        user_id (str): The user's unique ID.

    Returns:
        User: The User object if found, else None.
    """
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(
            user_id=str(user_data["_id"]),
            username=user_data["username"],
            password=user_data["password"],)
    return None


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    On GET request, renders the registration page.
    On POST request, processes the registration form and creates a new user.

    Returns:
        Response: Redirects to login page upon successful registration,
                  or renders registration page with error messages.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        repassword = request.form["repassword"]
        if password != repassword:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        if db.users.find_one({"username": username}):
            flash("Username already exists.")
            return redirect(url_for("register"))

        db.users.insert_one({"username": username, "password": hashed_password})
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.

    On GET request, renders the login page.
    On POST request, processes the login form and logs in the user.

    Returns:
        Response: Redirects to index page upon successful login,
                  or renders login page with error messages.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_data = db.users.find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(
                user_id=str(user_data["_id"]),
                username=user_data["username"],
                password=user_data["password"],
            )
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("index"))
        flash("Invalid username or password.")
        return redirect(url_for("login"))


# LOGOUT
@app.route("/logout")
@login_required
def logout():
    """
    Log out the current user and redirect to the login page.

    Returns:
        Response: Redirects to the login page with a logout message.
    """
    logout_user()
    session.pop("_flashes", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    """Render the homepage with mood summary data."""
    mood_entries = collection.find().sort("timestamp", -1).limit(100)
    entries = [
        {
            "file_name": entry["file_name"],
            "transcript": entry["transcript"],
            "sentiment": entry["sentiment"],
            "timestamp": entry["timestamp"],
        }
        for entry in mood_entries
    ]

    return render_template("index.html", entries=entries)


def convert_to_pcm_wav(input_file, output_file):
    """
    Convert an audio file to PCM WAV format using ffmpeg.

    Args:
        input_file (str): Path to the input audio file.
        output_file (str): Path to save the converted WAV file.

    Raises:
        RuntimeError: If ffmpeg fails to convert the file.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file, "-ar", "16000", "-ac", "1", output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}") from e


@app.route("/upload", methods=["POST"])
def upload_audio():
    """
    Handle audio file uploads from the frontend.
    Saves the file locally and forwards it to the machine learning client.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Generate unique filenames
    file_extension = os.path.splitext(audio_file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    converted_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"], f"converted_{unique_filename}"
    )

    try:
        audio_file.save(file_path)
    except IOError as io_error:
        return jsonify({"error": "Failed to save file", "details": str(io_error)}), 500

    try:
        # Convert the uploaded file to PCM WAV format
        convert_to_pcm_wav(file_path, converted_file_path)
    except RuntimeError as conversion_error:
        return (
            jsonify(
                {
                    "error": "Failed to convert file to PCM WAV",
                    "details": str(conversion_error),
                }
            ),
            500,
        )

    user_id = current_user.get_id()
    # Forward the **converted** file to the machine learning client
    try:
        with open(converted_file_path, "rb") as file_obj:
            response = requests.post(
                ML_CLIENT_URL,
                files={"audio": file_obj},
                data={"user_id": user_id},  # Pass the user_id to the ML client
                timeout=10,
            )

        if response.status_code == 200:

            return (
                jsonify(
                    {
                        "message": "File uploaded and processed successfully",
                        "data": response.json(),
                    }
                ),
                200,
            )

        return (
            jsonify({"error": "ML client failed", "details": response.json()}),
            response.status_code,
        )

    except requests.exceptions.RequestException as req_error:
        return (
            jsonify(
                {
                    "error": "Failed to forward file to ML client",
                    "details": str(req_error),
                }
            ),
            500,
        )


@app.route("/show_results")
@login_required
def show_results():
    """Render the results page."""
    return render_template("showResults.html")


@app.route("/api/mood-trends")
def mood_trends():
    """Provide mood trend data for visualization."""
    user_id = current_user.get_id()
    mood_counts = {
        "Positive": collection.count_documents(
            {"sentiment.mood": "Positive", "user_id": user_id}
        ),
        "Negative": collection.count_documents(
            {"sentiment.mood": "Negative", "user_id": user_id}
        ),
        "Neutral": collection.count_documents(
            {"sentiment.mood": "Neutral", "user_id": user_id}
        ),
    }
    return jsonify(mood_counts)


@app.route("/api/recent-entries")
@login_required
def recent_entries():
    """Provide recent entries data for the current user."""
    user_id = current_user.get_id()
    try:
        entries = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(100)
        entries_list = [
            {
                "_id": str(entry["_id"]),
                "file_name": entry.get("file_name", ""),
                "transcript": entry.get("transcript", ""),
                "sentiment": entry.get("sentiment", ""),
                "timestamp": (
                    entry.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(entry.get("timestamp"), datetime)
                    else entry.get("timestamp", "")
                ),
            }
            for entry in entries
        ]
        return jsonify(entries_list), 200
    except PyMongoError as mongo_error:
        # Log the error
        logging.error("Database error: %s", mongo_error)
        return jsonify({"error": "Database error occurred"}), 500

    except (TypeError, KeyError) as data_error:
        # Log the error
        logging.error("Data processing error: %s", data_error)
        return jsonify({"error": "Data processing error occurred"}), 500


@app.route("/delete-journal/<entry_id>", methods=["DELETE"])
def delete_journal(entry_id):
    """
    Deletes a journal entry by its ID.

    Args:
        entry_id (str): The ID of the entry to delete.

    Returns:
        JSON response indicating success or failure.
    """
    try:
        user_id = current_user.get_id()
        # Attempt to delete the document with the specified ObjectId and user_id
        result = collection.delete_one({"_id": ObjectId(entry_id), "user_id": user_id})

        if result.deleted_count > 0:
            return jsonify({"message": "Entry deleted successfully"}), 200

        # Entry not found in the collection
        return jsonify({"error": "Entry not found"}), 404

    except PyMongoError as mongo_error:
        # Handle MongoDB-specific errors
        return (
            jsonify({"error": "Database error occurred", "details": str(mongo_error)}),
            500,
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
