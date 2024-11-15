"""
This is a web app module for FaceBox
"""

import os
import base64
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import sys
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["attendify"]
users_collection = db["users"]

def decode_base64_image(image_data):
    try:
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes))
        image_path = os.path.join("uploads", "captured_image.jpg")
        image.save(image_path)
        print(f"Image decoded and saved successfully at: {image_path}")
        return image_path
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def encode_face(image_path):
    response = requests.post('http://ml-client:5000/encode_face', json={'image_path': image_path})
    return response.json()

def recognize_face(stored_encodings, test_image_path):
    response = requests.post('http://ml-client:5000/recognize_face', json={'stored_encodings': stored_encodings, 'test_image_path': test_image_path})
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

        image_path = decode_base64_image(image_data)
        if not image_path:
            return render_template("verify_result.html", result="Failed to process image")

        response = encode_face(image_path)
        if 'error' in response:
            return render_template("verify_result.html", result=response['error'])

        encoding_list = response['encoding']

        users_collection.insert_one({"encoding": encoding_list})
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        image_data = request.form.get("image_data")
        if not image_data:
            print("Debug: Image data not received or is empty.")
            return render_template("verify_result.html", result="Image capture failed")

        # Decode the image data
        image_path = decode_base64_image(image_data)
        if not image_path:
            print("Debug: Failed to decode the image data.")
            return render_template("verify_result.html", result="Failed to process image")

        print(f"Debug: Image saved successfully at {image_path}")

        # Retrieve all stored encodings from the database
        users = users_collection.find()
        stored_encodings = [user["encoding"] for user in users]

        # Perform facial recognition using ml_client
        response = recognize_face(stored_encodings, image_path)
        if 'error' in response:
            print(f"Debug: {response['error']}")
            return render_template("verify_result.html", result=response['error'])

        if response['result'] == "verified":
            session["username"] = "User"  # Customize this as needed
            return redirect(url_for("home"))
        elif response['result'] == "not_recognized":
            return render_template("verify_result.html", result="Face not recognized")
        else:
            return render_template("verify_result.html", result="No face detected in the image")

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)