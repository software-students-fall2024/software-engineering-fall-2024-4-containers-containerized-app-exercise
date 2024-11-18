"""
This application serves as the main entry point for the Flask web application,
connecting to MongoDB and providing the frontend interface.
"""

import os
from flask import Flask, render_template, jsonify, Response
from pymongo import MongoClient
from dotenv import load_dotenv
import cv2
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
