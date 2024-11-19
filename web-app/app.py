import os
import cv2
from flask import Flask, render_template, jsonify, Response
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.binary import Binary
import atexit
import datetime

# Flask app setup
app = Flask(__name__)

# MongoDB Atlas connection
uri = "mongodb+srv://raa9917:Rr12112002@cluster0.p902n.mongodb.net/?retryWrites=true&w=majority"
try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')  # Test the connection
    db = client["object_detection"]
    collection = db["detected_objects"]
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    db = None
    collection = None

# Initialize camera
camera = cv2.VideoCapture(0)
atexit.register(lambda: camera.release())


@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/capture_frame", methods=["POST"])
def capture_frame():
    """Capture a frame and save it to MongoDB."""
    if collection is None:
        return jsonify({"error": "Database not connected"}), 500

    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Failed to capture frame"}), 500

    # Encode the frame to JPEG format
    _, buffer = cv2.imencode(".jpg", frame)
    image_binary = Binary(buffer.tobytes())

    # Save to MongoDB
    document = {
        "image": image_binary,
        "timestamp": datetime.datetime.utcnow(),
        "status": "pending",  # Waiting for processing
        "detections": [],
    }
    result = collection.insert_one(document)
    return jsonify({"message": "Frame captured and saved", "id": str(result.inserted_id)}), 200


@app.route("/latest_detection", methods=["GET"])
def latest_detection():
    """Fetch the latest detection results from MongoDB."""
    if collection is None:
        return jsonify({"error": "Database not connected"}), 500

    try:
        detection = collection.find_one({"status": "processed"}, sort=[("timestamp", -1)])
        if not detection:
            return jsonify({"message": "No processed detections available"}), 404

        detections = detection.get("detections", [])
        return jsonify({"timestamp": detection["timestamp"], "labels": detections})
    except Exception as e:
        print(f"Error fetching detection: {e}")
        return jsonify({"error": "An error occurred while fetching detection data."}), 500


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
        else:
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
