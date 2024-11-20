"""
This module sets up the Flask application for the Plant Identifier project.
"""

import os
from bson import ObjectId
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    make_response,
    session,
    url_for,
)
import pymongo
from flask_cors import CORS
from werkzeug.utils import secure_filename
import base64
import requests
import uuid

load_dotenv()


def create_app():
    """Initializes and configures the Flask app"""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

    connection = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = connection[os.getenv("MONGO_DBNAME")]

    @app.route("/")
    def home():
        if request.args.get("user"):
            user_entries = list(db.plants.find())
            if len(user_entries) > 3:
                new_entries = [user_entries[-1], user_entries[-2], user_entries[-3]]
                user_entries = new_entries
            return render_template(
                "home.html", user=request.args.get("user"), user_entries=user_entries
            )
        return render_template("home.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            # password = request.form["password"]

            session["username"] = username

            return redirect(url_for("home", user=username))

        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            db.users.insert_one({"username": username, "password": password})
            session["username"] = username

            return redirect(url_for("home", user=username))

        return render_template("signup.html")


    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "POST":
            # Retrieve the base64-encoded image from the form
            photo_data = request.form.get("photo")
            if not photo_data:
                return "No photo data received", 400

            # Decode the base64 string to binary image data
            photo_data = photo_data.split(",")[1]  # Remove the "data:image/png;base64," prefix
            photo_binary = base64.b64decode(photo_data)

            # Ensure the directory exists
            try:
                uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                print(f"Uploads directory: {uploads_dir} (Exists: {os.path.exists(uploads_dir)})")
            except Exception as e:
                print(f"Failed to create directory {uploads_dir}: {e}")
                return "Directory creation failed", 500

            # Save the decoded image to a file
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(uploads_dir, filename)

            try:
                with open(filepath, "wb") as f:
                    f.write(photo_binary)
                print(f"File saved successfully: {filepath}")
            except Exception as e:
                print(f"Unexpected error while saving file: {e}")
                return "File save failed", 500

            try:
                # Send the saved image to the ML client
                ml_client_url = "http://ml-client:3001/predict"
                with open(filepath, "rb") as file:
                    files = {"image": (filename, file, "image/png")}
                    response = requests.post(ml_client_url, files=files)
                    response.raise_for_status()
                    result = response.json()
                    plant_name = result.get("plant_name", "Unknown")
                    res = {"photo": filename, "filepath": filepath, "plant_name": plant_name}

                    # Save the result to the database
                    db.predictions.insert_one(res)
            except Exception as e:
                print(f"Error: {e}")
                return "Error processing the photo", 500

            # Redirect to the results page with the filename
            return redirect(url_for("results", filename=filename))

        return render_template("upload.html")

    @app.route("/new_entry", methods=["GET", "POST"])
    def new_entry():
        new_entry_id = request.args.get("new_entry_id")
        entry = ObjectId(new_entry_id)
        if request.method == "POST":
            instructions = request.form["instructions"]
            db.plants.update_one(
                {"_id": entry}, {"$set": {"instructions": instructions}}
            )
            return redirect(url_for("home", user=session["username"]))
        document = db.plants.find_one({"_id": entry})
        photo = document["photo"]
        name = document["name"]
        return render_template(
            "new-entry.html", photo=photo, name=name, new_entry_id=new_entry_id
        )

    @app.route("/results/<filename>")
    def results(filename):
        """
        Fetch and display prediction results from MongoDB.
        """
        # Query MongoDB for the result associated with the given filename
        result = db.predictions.find_one({"photo": filename})
        if result:
            return render_template("results.html", result=result)
        return make_response("Result not found", 404)

    @app.route("/history")
    def history():
        """
        Display all prediction results from the database.
        """
        all_results = list(db.predictions.find())
        return render_template("history.html", results=all_results)

    return app


if __name__ == "__main__":
    # FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app = create_app()
    CORS(app)
    app.run(host="0.0.0.0", port=5000)
