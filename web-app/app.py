"""
This is the main module for the web app front end.
"""

import atexit
from datetime import datetime, timezone
import os

import cv2
from bson.binary import Binary
import requests
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]

# define ml service for docker
ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml-client:5001")

# Initialize camera
CAMERA = None  # pylint: disable=no-member
atexit.register(lambda: CAMERA.release() if CAMERA else None)  # pylint: disable=W0108


@app.route("/")
def index():
    """Index returns index home page HTML."""
    return render_template("index.html")


@app.route("/capture_and_process", methods=["POST"])  # pylint: disable=no-member
def capture_and_process():
    """Process a frame uploaded by the client."""
    # Check if a frame was uploaded
    if "frame" not in request.files:
        return jsonify({"error": "No frame provided"}), 400

    # Read the uploaded frame
    frame_file = request.files["frame"].read()
    np_frame = np.frombuffer(frame_file, np.uint8)
    frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)  # pylint: disable=no-member

    if frame is None:
        return jsonify({"error": "Invalid frame data"}), 400

    # Process the frame (e.g., save to MongoDB, send to ML client)
    _, buffer = cv2.imencode(".jpg", frame)  # pylint: disable=no-member
    image_binary = Binary(buffer)

    document = {
        "image": image_binary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "detections": [],
    }
    result = collection.insert_one(document)

    # Trigger processing in the ML app
    ml_response = requests.post(f"{ml_service_url}/process_pending", timeout=90)
    if ml_response.status_code != 200:
        return jsonify({"error": "Processing failed to reach ml service!"}), 500

    return (
        jsonify(
            {
                "message": "Frame captured and processed by ml service",
                "id": str(result.inserted_id),
                "detections": ml_response.json().get("detections", []),
            }
        ),
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
