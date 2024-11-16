"""
This is a web app for the Attendify project
"""

import os
import base64
import json  # Add this import
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import requests
import numpy as np
from io import BytesIO

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Max 16 MB upload size

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(mongo_uri)
db = client["attendify"]
users_collection = db["users"]


def decode_base64_image(image_data):
    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    return image_bytes


def encode_face(image_bytes):
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
    response = requests.post("http://ml-client:5000/encode_face", files=files)
    return response.json()


def recognize_face(stored_encodings, image_bytes):
    files = {"file": ("test_image.jpg", image_bytes, "image/jpeg")}
    # Serialize the stored_encodings to a JSON string
    data = {"stored_encodings": json.dumps(stored_encodings)}
    response = requests.post(
        "http://ml-client:5000/recognize_face", files=files, data=data
    )
    return response.json()


@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        image_data = request.form.get("image_data")
        if not image_data:
            return render_template("verify_result.html", result="Image capture failed")

        image_bytes = decode_base64_image(image_data)
        response = encode_face(image_bytes)
        if "error" in response:
            return render_template("verify_result.html", result=response["error"])

        encoding_list = response["encoding"]
        users_collection.insert_one({"encoding": encoding_list})
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        image_data = request.form.get("image_data")
        if not image_data:
            return render_template("verify_result.html", result="Image capture failed")

        image_bytes = decode_base64_image(image_data)
        users = users_collection.find()
        stored_encodings = [user["encoding"] for user in users]

        response = recognize_face(stored_encodings, image_bytes)
        if "error" in response:
            return render_template("verify_result.html", result=response["error"])

        if response["result"] == "verified":
            session["username"] = "User"
            return redirect(url_for("home"))
        else:
            return render_template("verify_result.html", result="Face not recognized")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
