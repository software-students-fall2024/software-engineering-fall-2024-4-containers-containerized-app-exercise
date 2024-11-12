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

def get_camera_data():
    """Fetch the image URL for a specific traffic camera using the 511 NY API."""
    url = f"https://511ny.org/api/getcameras?key=bd90c3a94f0f4ca2b1a44fdc9056e0d6&format=json
"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
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

def save_to_db(vehicle_count, camera_info):
    """Save the vehicle count data to MongoDB."""
    data = {
        "timestamp": datetime.utcnow(),
        "vehicle_count": vehicle_count,
        "camera_id": camera_info['ID'],
        "location": camera_info['Name']
    }
    traffic_data_collection.insert_one(data)
    print(f"Data saved to MongoDB: {data}")

def main():
    camera_data = get_camera_data()
    if not camera_data:
        return

    # Allow user to select a camera
    print("Available Cameras:")
    for idx, camera in enumerate(camera_data):
        print(f"{idx}: {camera['Name']}")

    camera_index = int(input("Enter the number of the camera you want to monitor: "))
    selected_camera = camera_data[camera_index]

    while True:
        img = fetch_image(selected_camera['Url'])
        if img is not None:
            # Process image and count vehicles
            vehicle_count = detect_vehicles(img)
            save_to_db(vehicle_count, selected_camera)
        
        # Wait before fetching the next image (adjust interval as needed)
        time.sleep(30)  # Fetch every 30 seconds

if __name__ == "__main__":
    main()


