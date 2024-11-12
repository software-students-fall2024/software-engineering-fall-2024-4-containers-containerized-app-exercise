import requests
import cv2
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import time


# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['traffic_db']
traffic_data_collection = db['traffic_data']

# Direct image URL
CAMERA_IMAGE_URL = "https://ie.trafficland.com/v2.0/2308/huge?system=weatherbug-cmn&pubto…019ffb4…&refreshRate=30000&rnd=1731276551337"
#API_KEY = 'bd90c3a94f0f4ca2b1a44fdc9056e0d6'

def get_camera_image_url():
    """Fetch the image URL for a specific traffic camera using the 511 NY API."""
    url = f"https://api.511ny.org/cameras?key=bd90c3a94f0f4ca2b1a44fdc9056e0d6&format=json&id={CAMERA_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        camera_data = response.json()
        # Extract the image URL from the JSON response (adapt based on actual JSON structure)
        image_url = camera_data['cameras'][0]['url']
        return image_url
    else:
        print("Failed to fetch camera data.")
        return None
    

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


