import os
import base64
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from gridfs import GridFS
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
fs = GridFS(db)  # GridFS instance
users_collection = db["users"]

def decode_base64_image_to_gridfs(image_data):
    try:
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_bytes))
        output = BytesIO()
        image.save(output, format="JPEG")
        image_id = fs.put(output.getvalue(), content_type="image/jpeg")
        print(f"Image successfully stored in GridFS with ID: {image_id}")
        return image_id
    except Exception as e:
        print(f"Error decoding and storing image: {e}")
        return None


def get_image_from_gridfs(image_id):
    """
    Retrieve an image from GridFS using its ID.
    Returns the image as a file-like object.
    """
    try:
        grid_out = fs.get(image_id)
        return BytesIO(grid_out.read())
    except Exception as e:
        print(f"Error retrieving image from GridFS: {e}")
        return None

def encode_face(image_id):
    """
    Send a request to the ML service with the image stored in GridFS.
    """
    image_bytes = get_image_from_gridfs(image_id)
    if not image_bytes:
        print("Debug: Failed to retrieve image from GridFS.")
        return {"error": "Failed to retrieve image from GridFS"}

    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post('http://ml-client:5000/encode_face', files=files, timeout=10)
        print(f"Debug: Response status code: {response.status_code}")
        print(f"Debug: Response text: {response.text}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Debug: ML service request failed: {e}")
        return {"error": "ML service request failed"}
    except requests.exceptions.JSONDecodeError:
        print("Debug: Failed to decode JSON response from ML service.")
        return {"error": "Invalid JSON response from ML service"}


def recognize_face(stored_encodings, test_image_id):
    """
    Send a request to the ML service for face recognition.
    """
    test_image_bytes = get_image_from_gridfs(test_image_id)
    if not test_image_bytes:
        return {"error": "Failed to retrieve test image from GridFS"}

    files = {'file': ('test_image.jpg', test_image_bytes, 'image/jpeg')}
    payload = {'stored_encodings': stored_encodings}
    response = requests.post('http://ml-client:5000/recognize_face', files=files, data=payload)
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

        # Save image to GridFS
        image_id = decode_base64_image_to_gridfs(image_data)
        if not image_id:
            return render_template("verify_result.html", result="Failed to process image")

        response = encode_face(image_id)
        if 'error' in response:
            return render_template("verify_result.html", result=response['error'])

        encoding_list = response['encoding']

        # Store encoding and image_id in MongoDB
        users_collection.insert_one({"encoding": encoding_list, "image_id": image_id})
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        image_data = request.form.get("image_data")
        if not image_data:
            print("Debug: Image data not received or is empty.")
            return render_template("verify_result.html", result="Image capture failed")

        # Save image to GridFS
        test_image_id = decode_base64_image_to_gridfs(image_data)
        if not test_image_id:
            print("Debug: Failed to decode the image data.")
            return render_template("verify_result.html", result="Failed to process image")

        print(f"Debug: Test image stored in GridFS with ID: {test_image_id}")

        # Retrieve all stored encodings from the database
        users = users_collection.find()
        stored_encodings = [user["encoding"] for user in users]

        # Perform facial recognition using ML service
        response = recognize_face(stored_encodings, test_image_id)
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
