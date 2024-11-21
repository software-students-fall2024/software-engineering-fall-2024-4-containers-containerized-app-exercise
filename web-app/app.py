"""
This module sets up the Flask application for the Plant Identifier project.
"""

import base64
import os
import uuid

from bson import ObjectId
from bson.errors import InvalidId  # Added import
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    make_response,
    session,
    url_for,
    send_from_directory,
)
import pymongo
import requests
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()


def create_app():
    """Initializes and configures the Flask app."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit
    secret_key = os.getenv("SECRET_KEY", "supersecretkey")
    if not secret_key:
        raise ValueError("No SECRET_KEY set for Flask application")
    app.secret_key = secret_key

    connection = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = connection[os.getenv("MONGO_DBNAME")]
    app.db = db  # Attach db to app for easy access in routes

    register_routes(app, db)

    return app


def register_routes(app, db):
    """Registers all the routes for the Flask app."""

    @app.route("/")
    def home():
        """Render the home page."""
        user = request.args.get("user")
        if user:
            user_entries = list(db.plants.find().sort("_id", pymongo.DESCENDING))
            user_entries = user_entries[:3]  # Get the latest three entries
            return render_template("home.html", user=user, user_entries=user_entries)
        return render_template("home.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle user login."""
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            user = db.users.find_one({"username": username})
            if user and check_password_hash(user["password"], password):
                session["username"] = username
                return redirect(url_for("home", user=username))
            return render_template(
                "login.html", error="Invalid credentials"
            )  # Removed 'else'

        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        """Handle user signup."""
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            if db.users.find_one({"username": username}):
                return render_template("signup.html", error="Username already exists")

            hashed_password = generate_password_hash(password)
            db.users.insert_one({"username": username, "password": hashed_password})
            session["username"] = username

            return redirect(url_for("home", user=username))

        return render_template("signup.html")

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        """Handle image upload and processing."""
        if request.method == "POST":
            photo_data = request.form.get("photo")
            if not photo_data:
                return handle_error("No photo data received", 400)

            try:
                photo_binary = decode_photo(photo_data)
            except ValueError as error:
                print(f"Invalid photo data: {error}")
                return handle_error("Invalid photo data", 400)

            try:
                filepath, filename = save_photo(photo_binary)
            except IOError as error:
                print(f"Error saving file: {error}")
                return handle_error("File save failed", 500)

            try:
                process_photo(app=db, filepath=filepath, filename=filename)
            except (requests.RequestException, pymongo.errors.PyMongoError) as error:
                print(f"Processing error: {error}")
                return handle_error("Error processing the photo", 500)

            return redirect(url_for("results", filename=filename))

        return render_template("upload.html")

    @app.route("/new_entry", methods=["GET", "POST"])
    def new_entry():
        """Handle adding new instructions to an entry."""
        new_entry_id = request.args.get("new_entry_id")
        if not new_entry_id:
            return handle_error("No entry ID provided", 400)

        try:
            entry_id = ObjectId(new_entry_id)
        except InvalidId:  # Changed from Exception to InvalidId
            return handle_error("Invalid entry ID", 400)

        if request.method == "POST":
            instructions = request.form["instructions"]
            db.plants.update_one(
                {"_id": entry_id}, {"$set": {"instructions": instructions}}
            )
            return redirect(url_for("home", user=session.get("username")))

        document = db.plants.find_one({"_id": entry_id})
        if not document:
            return handle_error("Entry not found", 404)

        photo = document.get("photo")
        name = document.get("name")
        return render_template(
            "new-entry.html", photo=photo, name=name, new_entry_id=new_entry_id
        )

    @app.route("/results/<filename>")
    def results(filename):
        """Fetch and display prediction results from MongoDB."""
        result = db.predictions.find_one({"photo": filename})
        if result:
            return render_template("results.html", result=result)
        return handle_error("Result not found", 404)

    @app.route("/history")
    def history():
        """Display all prediction results from the database."""
        all_results = list(db.predictions.find().sort("_id", pymongo.DESCENDING))
        return render_template("history.html", results=all_results)

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        """Serve uploaded files."""
        uploads_dir = os.path.join(app.root_path, "static", "uploads")
        return send_from_directory(uploads_dir, filename)


def decode_photo(photo_data):
    """Decodes base64 photo data."""
    try:
        photo_data = photo_data.split(",")[1]  # Remove the data URL prefix
        return base64.b64decode(photo_data)
    except (IndexError, ValueError) as error:
        raise ValueError("Invalid photo data") from error


def save_photo(photo_binary):
    """Saves the decoded photo to the uploads directory."""
    uploads_dir = os.path.join("static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(uploads_dir, filename)

    with open(filepath, "wb") as file_handle:
        file_handle.write(photo_binary)
    print(f"File saved successfully: {filepath}")

    return filepath, filename


def process_photo(app, filepath, filename):
    """Sends the photo to the ML client and saves the prediction to MongoDB."""
    ml_client_url = "http://ml-client:3001/predict"
    with open(filepath, "rb") as file_handle:
        files = {"image": (filename, file_handle, "image/png")}
        response = requests.post(
            ml_client_url, files=files, timeout=10
        )  # Added timeout
        response.raise_for_status()
        result = response.json()
        plant_name = result.get("plant_name", "Unknown")
        res = {
            "photo": filename,
            "filepath": filepath,
            "plant_name": plant_name,
        }

        # Save the result to the database
        app.db.predictions.insert_one(res)
        print(f"Inserted prediction into MongoDB: {res}")


def handle_error(message, status_code):
    """Handles errors by returning a response with a message and status code."""
    return make_response(render_template("error.html", message=message), status_code)


if __name__ == "__main__":
    APP = create_app()
    APP.run(host="0.0.0.0", port=5000)
