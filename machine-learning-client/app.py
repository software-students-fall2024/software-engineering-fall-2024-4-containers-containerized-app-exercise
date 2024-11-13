"""
This application serves as the main entry point for the machine learning client,
connecting to MongoDB and performing data analysis tasks.
"""

import os
import base64
from datetime import datetime
import numpy as np
import cv2
import tensorflow as tf
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

mongo = MongoClient(os.getenv("MONGODB_URI"))
db = mongo["object_detection"]

# load MobileNet model and labels
model = tf.keras.applications.MobileNetV2(weights="imagenet")
decode_predictions = tf.keras.applications.mobilenet_v2.decode_predictions


def preprocess_image(image):
    """Preprocess the image for MobileNet input."""
    image = tf.image.resize(image, (224, 224))
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return np.expand_dims(image, axis=0)


def detect_objects(image):
    """Detect objects using MobileNet and return top predictions."""
    preprocessed_image = preprocess_image(image)
    predictions = model.predict(preprocessed_image)
    decoded_predictions = decode_predictions(predictions, top=3)[
        0
    ]  # get top 3 predictions
    detected_objects = [
        {"label": label, "confidence": float(conf)}
        for (_, label, conf) in decoded_predictions
    ]
    return detected_objects


def encode_image(image_array):
    """Encode image to base64."""
    _, buffer = cv2.imencode(".png", image_array)
    return base64.b64encode(buffer).decode("utf-8")


@app.route("/api/detect", methods=["POST"])
def detect():
    """Main endpoint for image detection."""
    if "file" not in request.files:
        return "No image file provided.", 400

    # read and decode the image file
    image_file = request.files["file"]
    image_array = np.frombuffer(image_file.read(), np.uint8)
    image = tf.image.decode_image(image_array, channels=3)

    # detect objects
    detected_objects = detect_objects(image)

    # convert the image for storage/display in mongo
    _, buffer = cv2.imencode(".png", np.array(image))
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    # Save to MongoDB
    detection_data = {
        "timestamp": datetime.now(),
        "detected_objects": detected_objects,
        "image": encoded_image,
    }
    db.detections.insert_one(detection_data)

    return jsonify(detection_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
