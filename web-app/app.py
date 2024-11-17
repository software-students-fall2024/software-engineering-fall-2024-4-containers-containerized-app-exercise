"""
This application serves as the main entry point for the Flask web application,
connecting to MongoDB and providing the frontend interface.
"""

import os
from flask import Flask, render_template, jsonify, Response  # Move Response here
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]

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
    # You can add logic to render a dashboard here
    return render_template("dashboard.html")  # Ensure you have a 'dashboard.html' template

# API route for object detection
@app.route("/api/detect", methods=["POST"])
def api_detect():
    """Object detection API endpoint"""
    # Your object detection logic here, for now return 'objects'
    return jsonify({"status": "success", "message": "Object detection results here", "objects": []})

from flask import Response

@app.route('/video_feed')
def video_feed():
    """Stream the video feed."""
    # Logic to stream video from a camera or return a sample video frame
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_video():
    """Generate video frames for streaming (replace with your actual video generation logic)."""
    while True:
        # This is just a placeholder. Replace it with your actual video capture code.
        frame = get_video_frame()  # Capture or retrieve the video frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def get_video_frame():
    """Get a single video frame (replace this with your actual frame capture logic)."""
    # For now, this returns an empty byte string. Replace with real image capture.
    return b""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
