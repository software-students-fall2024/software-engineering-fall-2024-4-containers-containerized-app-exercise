"""
This application serves as the main entry point for the machine learning client,
connecting to MongoDB and performing data analysis tasks.
"""

import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
import pymongo
import base64
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime

load_dotenv()
uri = os.environ["MONGODB_URI"]
mongo = MongoClient(uri, server_api=ServerApi("1"))

try:
    mongo.admin.command("ping")
    print("Successfully connected to MongoDB.")
except pymongo.errors.ConnectionFailure as e:
    print(f"MongoDB connection failed: {e}")

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# load YOLO model
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]


def detect_objects(image):
    """Detect objects in the provided image and draw bounding boxes."""
    height, width = image.shape
    blob = cv2.dnn.blobFromImage(
        image, 0.00392, (416, 416), (0, 0, 0), True, crop=False
    )
    net.setInput(blob)
    detections = net.forward(output_layers)
    labels = []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = int(np.argmax(scores))
            confidence = scores[class_id]
            if confidence > 0.5:
                label = classes[class_id]
                labels.append(label)

                # bounding box coords and draw
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                w = int(obj[2] * width)
                h = int(obj[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # draw the bounding box and label
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    image,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

    return labels, image


@app.route("/api/detect", methods=["POST"])
def detect():
    """Receive an image, detect objects, and return image with bounding boxes."""
    files = request.files
    if "file" not in files:
        return "No image file provided.", 400

    image_file = files["file"]
    image_array = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # detect objects and draw bounding boxes
    detected_objects, processed_image = detect_objects(image)

    if not detected_objects:
        return jsonify({"message": "No objects detected."}), 200

    # encode the processed image with bounding boxes
    _, buffer = cv2.imencode(".png", processed_image)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    # save detection data to mongo
    detection_data = {
        "timestamp": datetime.now(),
        "detected_objects": detected_objects,
        "image": encoded_image,  # store image as base64-encoded string
    }
    mongo.db.detections.insert_one(detection_data)

    return jsonify(detection_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
