import time
from datetime import datetime
from io import BytesIO

import torch
from flask import Flask, jsonify
from PIL import Image
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection
uri = (
    "mongodb+srv://raa9917:Rr12112002@cluster0.p902n.mongodb.net/"
    "?retryWrites=true&w=majority"
)
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["object_detection"]
collection = db["detected_objects"]

# Initialize Flask app
app = Flask(__name__)

# Load YOLOv5 model
model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True).to("cpu")


def detect_objects(image):
    """Perform object detection on the provided image."""
    results = model(image)
    detections = results.pandas().xyxy[0].to_dict(orient="records")
    return [
        {"label": det["name"], "confidence": float(det["confidence"])}
        for det in detections
    ]


@app.route("/")
def index():
    """Health check endpoint for the ML app."""
    return jsonify({"status": "running"}), 200


def process_pending_images():
    """Periodically process pending images from MongoDB."""
    while True:
        try:
            # Find a document with status "pending"
            document = collection.find_one({"status": "pending"})
            if document:
                print("Processing a pending frame...")

                # Decode the image
                image_data = BytesIO(document["image"])
                image = Image.open(image_data)

                # Perform object detection
                detections = detect_objects(image)

                # Update the document with detections
                collection.update_one(
                    {"_id": document["_id"]},
                    {
                        "$set": {
                            "status": "processed",
                            "detections": detections,
                            "processed_at": datetime.utcnow(),
                        }
                    },
                )
                print(
                    f"Processed frame: {document['_id']} "
                    f"with detections: {detections}"
                )
            else:
                print("No pending frames. Retrying...")
        except Exception as e:
            print(f"Error processing pending frames: {e}")

        time.sleep(5)  # Wait for 5 seconds before checking again


if __name__ == "__main__":
    # Start automatic processing
    print("Starting the automatic frame processing...")
    process_pending_images()
