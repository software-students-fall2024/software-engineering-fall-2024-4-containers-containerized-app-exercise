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

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../machine_learning_client")
    )
)

import ml_client

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
            return render_template(
                "verify_result.html", result="Failed to process image"
            )

        encoding, error = ml_client.encode_face(image_path)
        if error:
            return render_template("verify_result.html", result=error)

        encoding_list = encoding.tolist()

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

        image_path = decode_base64_image(image_data)
        if not image_path:
            print("Debug: Failed to decode the image data.")
            return render_template(
                "verify_result.html", result="Failed to process image"
            )

        users = users_collection.find()
        stored_encodings = [user["encoding"] for user in users]

        result, error = ml_client.recognize_face(stored_encodings, image_path)
        if error:
            print(f"Debug: {error}")
            return render_template("verify_result.html", result=error)

        if result == "verified":
            session["username"] = "User"
            return redirect(url_for("home"))
        elif result == "not_recognized":
            return render_template("verify_result.html", result="Face not recognized")
        else:
            return render_template(
                "verify_result.html", result="No face detected in the image"
            )

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
