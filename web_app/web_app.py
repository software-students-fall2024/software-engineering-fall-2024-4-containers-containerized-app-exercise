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
        elif not image_data:
            error = "Image capture failed."
        else:
            existing_user = users_collection.find_one({"email": email})
            if existing_user:
                error = "Email is already registered."
            else:
                existing_username = users_collection.find_one({"username": username})
                if existing_username:
                    error = "Username is already taken."

        if error:
            return render_template("signup.html", error=error)

        # Hash the password
        hashed_password = generate_password_hash(password)

        image_bytes = decode_base64_image(image_data)
        response = encode_face(image_bytes)
        if "error" in response:
            return render_template("verify_result.html", result=response["error"])

        encoding_list = response["encoding"]

        # Insert the new user into the database
        users_collection.insert_one(
            {
                "username": username,
                "email": email,
                "password": hashed_password,
                "encoding": encoding_list,
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
        if "username" in request.form and "password" in request.form:
            # Handle username/password login
            username = request.form.get("username", "").strip()
            password = request.form.get("password")
            error = None

            if not username or not password:
                error = "Username and Password are required."
                return render_template("login.html", error=error)

            user = users_collection.find_one({"username": username})
            if user and check_password_hash(user["password"], password):
                session["username"] = username
                return redirect(url_for("home"))
            else:
                error = "Invalid username or password."
                return render_template("login.html", error=error)

        elif "image_data" in request.form:
            # Handle facial recognition login
            image_data = request.form.get("image_data")
            if not image_data:
                return render_template(
                    "verify_result.html", result="Image capture failed"
                )

            image_bytes = decode_base64_image(image_data)
            users = list(users_collection.find())
            stored_encodings = [user["encoding"] for user in users]

            response = recognize_face(stored_encodings, image_bytes)
            print("recognize_face response:", response)  # Debug print
            if "error" in response:
                return render_template("verify_result.html", result=response["error"])

            if response["result"] == "verified":
                matched_index = response.get("matched_index")
                print("matched_index:", matched_index)  # Debug print
                if matched_index is not None:
                    matched_index = int(matched_index)
                    if 0 <= matched_index < len(users):
                        matched_user = users[matched_index]
                        print("matched_user:", matched_user)  # Debug print
                        print("matched_user keys:", matched_user.keys())  # Debug print
                        session["username"] = matched_user["username"]
                        return redirect(url_for("home"))
                else:
                    return render_template(
                        "verify_result.html",
                        result="Face recognized but user not found",
                    )
            else:
                return render_template(
                    "verify_result.html", result="Face not recognized"
                )
        else:
            # Invalid form submission
            error = "Invalid login attempt."
            return render_template("login.html", error=error)

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
