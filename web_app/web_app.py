"""
This is the web application code.
"""

import os
import base64
import json
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Max 16 MB upload size

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(mongo_uri)
db = client["attendify"]
users_collection = db["users"]


def decode_base64_image(image_data):
    """
    Decode base64 image data to bytes
    """
    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return image_bytes


def encode_face(image_bytes):
    """
    Encode face from image bytes
    """
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
    response = requests.post(
        "http://ml-client:5000/encode_face", files=files, timeout=10
    )
    return response.json()


def recognize_face(stored_encodings, image_bytes):
    """
    Recognize face from image bytes
    """
    files = {"file": ("test_image.jpg", image_bytes, "image/jpeg")}
    data = {"stored_encodings": json.dumps(stored_encodings)}
    response = requests.post(
        "http://ml-client:5000/recognize_face", files=files, data=data, timeout=10
    )
    return response.json()


@app.route("/")
def welcome():
    """
    Welcome page
    """
    return render_template("welcome.html")


@app.route("/home")
def home():
    """
    Home page
    """
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Signup page
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password")
        image_data = request.form.get("image_data")
        error = None

        if not username or not email or not password:
            error = "Username, Email, and Password are required."
            return render_template("signup.html", error=error)

        if users_collection.find_one({"email": email}):
            error = "Email is already registered."
            return render_template("signup.html", error=error)

        if users_collection.find_one({"username": username}):
            error = "Username is already taken."
            return render_template("signup.html", error=error)

        if not image_data:
            error = "Image data is required."
            return render_template("signup.html", error=error)

        image_bytes = decode_base64_image(image_data)
        response = encode_face(image_bytes)
        if "error" in response:
            return render_template("signup.html", error=response["error"])

        encoding = response["encoding"]
        hashed_password = generate_password_hash(password)
        users_collection.insert_one(
            {
                "username": username,
                "email": email,
                "password": hashed_password,
                "encoding": encoding,
            }
        )

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page
    """
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")
        image_data = request.form.get("image_data")
        error = None

        if not username or not password or not image_data:
            error = "Username, password, and facial recognition are required."
            return render_template("login.html", error=error)

        user = users_collection.find_one({"username": username})

        if not user:
            error = "User not found."
            return render_template("login.html", error=error)

        # Check password
        if not check_password_hash(user["password"], password):
            error = "Invalid password."
            return render_template("login.html", error=error)

        # Check facial recognition
        image_bytes = decode_base64_image(image_data)
        stored_encoding = user.get("encoding")

        if not stored_encoding:
            return render_template(
                "login.html", error="No facial data found for this user."
            )

        response = recognize_face([stored_encoding], image_bytes)
        if "error" in response:
            return render_template("login.html", error=response["error"])

        if response["result"] == "verified":
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Face not recognized.")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    """
    Logout route
    """
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
