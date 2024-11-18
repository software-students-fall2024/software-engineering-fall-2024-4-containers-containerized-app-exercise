"""
This application serves as the main entry point for the Flask web application,
connecting to MongoDB and providing the frontend interface.
"""

import os
from flask import Flask, render_template, jsonify, Response, request
from pymongo import MongoClient
from dotenv import load_dotenv
import cv2
import requests
import atexit

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]

# Initialize video capture
camera = cv2.VideoCapture(0)  # Replace 0 with the camera index or video file path

# Ensure the camera is released when the application stops
atexit.register(lambda: camera.release())

ML_CLIENT_URL = "http://localhost:3001/api/detect"

def detect_with_ml_client(image_path):
    """Send an image to the machine-learning-client for detection."""
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(ML_CLIENT_URL, files=files)
        response.raise_for_status()  # Raise an error for failed requests
        return response.json()
    
# Index route
@app.route("/")
def index():
    """Index returns index home page html"""
    return render_template("index.html")


# Data route
@app.route("/data")
def get_data():
    """Fetch data from MongoDB"""
    data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB IDs
    return jsonify(data)


# Dashboard route
@app.route("/dashboard")
def dashboard():
    """Dashboard page"""
    return render_template("dashboard.html")

@app.route('/latest_detection', methods=['POST'])
def latest_detection():
    """Endpoint to detect objects using the ML client."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    image = request.files['file']
    image_path = f"/tmp/{image.filename}"
    image.save(image_path)

    try:
        detection_results = detect_with_ml_client(image_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(detection_results), 200

# Video feed route
@app.route("/video_feed")
def video_feed():
    """Stream the video feed."""
    return Response(
        generate_video(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def generate_video():
    """Generate video frames for streaming."""
    while True:
        frame = get_video_frame()  # Capture or retrieve the video frame
        if frame:
            yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"


def get_video_frame():
    """Capture a single video frame."""
    success, frame = camera.read()
    if not success:
        return b""
    # Encode frame as JPEG
    _, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()


# Main entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
