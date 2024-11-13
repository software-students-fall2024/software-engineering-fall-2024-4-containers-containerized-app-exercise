"""
This application serves as the main entry point for the machine learning client,
connecting to MongoDB and performing data analysis tasks.
"""

import os
from io import BytesIO
from datetime import datetime
import base64
import torch
from PIL import Image
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

mongo = MongoClient(os.getenv("MONGODB_URI"))
db = mongo["object_detection"]

# load YOLOv5 model
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)


def detect_objects(image):
    """Detect objects using YOLOv5"""
    results = model(image)
    detections = results.pandas().xyxy[0].to_dict(orient="records")
    return [
        {"label": det["name"], "confidence": float(det["confidence"])}
        for det in detections
    ]


@app.route("/api/detect", methods=["POST"])
def detect():
    """POST route for image file processing"""
    if "file" not in request.files:
        return "No image file provided.", 400

    # read image in
    image_file = request.files["file"]
    image = Image.open(image_file.stream)

    # detect objects
    detected_objects = detect_objects(image)

    # encode image to base64 for mongo storage
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # save to mongo
    detection_data = {
        "timestamp": datetime.now(),
        "detected_objects": detected_objects,
        "image": encoded_image,
    }
    result = db.detections.insert_one(detection_data)
    detection_data["_id"] = str(result.inserted_id)

    return jsonify(detection_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
