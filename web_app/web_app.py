"""
This is a web app module for Attendify
"""

import os
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  # Add this import
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["test_db"]
users_collection = db["users"]
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def login_required(f):
    """to log in"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def home():
    """to handles the home route."""
    username = session.get("username")
    return render_template("home.html", username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """handles user signup by collecting credentials and storing them with a face encoding."""
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            image = request.files.get("image")

            if not username or not password or not image:
                return "Missing required fields", 400

            # Save the uploaded image
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Send the image to the ML client for encoding
            ml_client_url = "http://localhost:5001/encode"
            response = requests.post(
                ml_client_url, json={"image_path": image_path}, timeout=10
            )
            if response.status_code != 200:
                return render_template(
                    "encode_result.html", error="Failed to encode image"
                )

            face_encoding = response.json().get("encoding")
            if not face_encoding:
                return render_template(
                    "encode_result.html", error="No face found in the image"
                )

            # Store user details in MongoDB
            users_collection.insert_one(
                {
                    "username": username,
                    "password": hashed_password,
                    "image_path": image_path,
                    "encoding": face_encoding,
                }
            )
            return redirect(url_for("login"))

        except (KeyError, requests.RequestException, ValueError) as e:
            print(f"Error during signup: {str(e)}")
            return render_template("encode_result.html", error="Internal Server Error")

    return render_template("signup.html")


@app.route("/verify", methods=["POST"])
@login_required
def verify():
    """handles face verification by comparing a new image with the stored face encoding."""
    try:
        username = session["username"]
        user = users_collection.find_one({"username": username})

        if not user:
            return render_template("verify_result.html", error="User not found")

        image = request.files.get("image")
        if not image:
            return render_template(
                "verify_result.html", error="Image is required for verification"
            )

        # Save the uploaded image for verification
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

        # Send the image to the ML client for verification
        ml_client_url = "http://localhost:5001/verify"
        response = requests.post(
            ml_client_url,
            json={"image_path": image_path, "stored_encoding": user["encoding"]},
            timeout=10,
        )
        if response.status_code != 200:
            return render_template(
                "verify_result.html", error="Failed to verify identity"
            )

        result = response.json().get("result")
        return render_template("verify_result.html", result=result)

    except (KeyError, requests.RequestException, ValueError) as e:
        print(f"Error during verification: {str(e)}")
        return render_template("verify_result.html", error="Internal Server Error")


@app.route("/login", methods=["GET", "POST"])
def login():
    """for users to log in"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid username or password"

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """for users to log out"""
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
