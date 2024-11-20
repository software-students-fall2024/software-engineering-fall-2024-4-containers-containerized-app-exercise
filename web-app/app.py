"""
This is the main module for the web app front end.
"""

import atexit
import datetime
import os
import threading
import time

import cv2
from bson.binary import Binary
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template
from pymongo import MongoClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]

# Initialize camera
camera = cv2.VideoCapture(0)  # pylint: disable=no-member
atexit.register(lambda: camera.release()) # pylint: disable=W0108


@app.route("/")
def index():
    """Index returns index home page HTML."""
    return render_template("index.html")


@app.route("/data")
def get_data():
    """Fetch data from MongoDB."""
    data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB IDs
    return jsonify(data)


@app.route("/dashboard")
def dashboard():
    """Dashboard page."""
    return render_template("dashboard.html")


@app.route("/capture_frame", methods=["POST"])
def capture_frame():
    """Capture a frame and save it to MongoDB."""
    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Failed to capture frame"}), 500

    # Encode the frame to JPEG format
    _, buffer = cv2.imencode(".jpg", frame)  # pylint: disable=no-member
    image_binary = Binary(buffer.tobytes())

    # Save to MongoDB
    document = {
        "image": image_binary,
        "timestamp": datetime.datetime.utcnow(),
        "status": "pending",  # Waiting for processing
        "detections": [],
    }
    result = collection.insert_one(document)
    return (
        jsonify({"message": "Frame captured and saved", "id": str(result.inserted_id)}),
        200,
    )


@app.route("/latest_detection", methods=["GET"])
def latest_detection():
    """Fetch the latest detection results from MongoDB."""
    detection = collection.find_one(
        {"status": "processed"},
        sort=[("timestamp", -1)],
    )
    if not detection:
        return jsonify({"message": "No processed detections available"}), 404

    detections = detection.get("detections", [])
    return jsonify({"timestamp": detection["timestamp"], "labels": detections})


@app.route("/video_feed")
def video_feed():
    """Stream the video feed."""
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def generate_frames():
    """Generate video frames for streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)  # pylint: disable=no-member
        frame = buffer.tobytes()
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


def capture_frames_periodically():
    """Background thread to capture frames every 5 seconds."""
    while True:
        time.sleep(5)
        try:
            with app.test_client() as client:
                client.post("/capture_frame")
                print("Frame captured and sent to MongoDB.")
        except Exception as e:
            print(f"Error capturing frame: {e}")


# Start the background thread when the app starts
threading.Thread(target=capture_frames_periodically, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
