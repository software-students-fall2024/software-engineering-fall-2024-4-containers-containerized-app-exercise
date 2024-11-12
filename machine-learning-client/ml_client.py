import requests
import cv2
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# MongoDB setup
load_dotenv()
uri = os.getenv("uri")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['traffic_db']
traffic_data_collection = db['traffic_data']

# Direct image URL
CAMERA_IMAGE_URL = "https://ie.trafficland.com/v2.0/2308/huge?system=weatherbug-cmn&pubto…019ffb4…&refreshRate=30000&rnd=1731276551337"

def fetch_image():
    """Fetch the image from the traffic camera."""
    response = requests.get(CAMERA_IMAGE_URL, stream=True)
    if response.status_code == 200:
        image_data = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        return img
    else:
        print("Failed to fetch image.")
        return None

def detect_vehicles(img):
    """Dummy vehicle detection function for demonstration."""
    # Placeholder for real object detection (e.g., using a model like YOLO)
    vehicle_count = 0  # Update this with actual vehicle detection code
    return vehicle_count

def save_to_db(vehicle_count):
    """Save the vehicle count data to MongoDB."""
    data = {
        "timestamp": datetime.utcnow(),
        "vehicle_count": vehicle_count,
        "location": "5th Ave @ 42nd St, NYC"
    }
    traffic_data_collection.insert_one(data)
    print(f"Data saved to MongoDB: {data}")

def main():
    while True:
        img = fetch_image()
        if img is not None:
            # Process image and count vehicles
            vehicle_count = detect_vehicles(img)
            save_to_db(vehicle_count)
        
        # Wait before fetching the next image (adjust interval as needed)
        time.sleep(30)  # Fetch every 30 seconds

if __name__ == "__main__":
    main()


