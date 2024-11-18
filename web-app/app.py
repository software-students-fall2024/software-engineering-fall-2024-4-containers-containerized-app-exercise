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
CAPTURED_IMAGE_PATH = 'static/captured_image.jpg'

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]

# Initialize video capture
camera = cv2.VideoCapture(0)  # Replace 0 with the camera index or video file path

# Ensure the camera is released when the application stops
atexit.register(lambda: camera.release())

ML_CLIENT_URL = "http://ml-client:3001/api/detect"  # Adjusted for Docker networking

def detect_with_ml_client(image_path):
    """Send an image to the machine-learning-client for detection."""
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        response = requests.post(ML_CLIENT_URL, files=files)
        response.raise_for_status()  # Raise an error for failed requests
        return response.json()

@app.route("/")
def index():
    """Render the main dashboard."""
    return render_template("index.html")

@app.route('/capture', methods=['POST'])
def capture():
    """Capture a single frame and send it to the detection client."""
    success, frame = camera.read()
    if not success:
        return jsonify({'error': 'Failed to capture frame'}), 500

    # Save the frame temporarily
    temp_image_path = CAPTURED_IMAGE_PATH
    cv2.imwrite(temp_image_path, frame)

    # Send the image to the machine-learning client
    try:
        response = detect_with_ml_client(temp_image_path)
        return jsonify({
            'message': 'Screenshot captured and processed!',
            'detections': response.get('detected_objects', [])
        }), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Detection failed', 'details': str(e)}), 500

@app.route("/video_feed")
def video_feed():
    """Stream the video feed."""
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

def generate_frames():
    """Generate video frames for the live feed."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
