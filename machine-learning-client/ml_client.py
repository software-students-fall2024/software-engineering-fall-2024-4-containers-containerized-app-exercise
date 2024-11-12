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

#API_KEY = 'bd90c3a94f0f4ca2b1a44fdc9056e0d6'

YOLO_CONFIG_PATH = "machine-learning-client/yolov3.cfg"            # Path to YOLO config file
YOLO_WEIGHTS_PATH = "machine-learning-client/yolov3.weights"       # Path to YOLO weights file
YOLO_CLASSES_PATH = "machine-learning-client/coco.names"  

net = cv2.dnn.readNetFromDarknet(YOLO_CONFIG_PATH, YOLO_WEIGHTS_PATH)
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

with open(YOLO_CLASSES_PATH, "r") as f:
    classes = [line.strip() for line in f.readlines()]

def get_camera_data():
    """Fetch the image URL for a specific traffic camera using the 511 NY API."""
    url = f"https://511ny.org/api/getcameras?key=bd90c3a94f0f4ca2b1a44fdc9056e0d6&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch camera data.")
        return None
    

def fetch_image(image_url):
    """Fetch the image from the traffic camera URL."""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_data = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        return img
    else:
        print("Failed to fetch image.")
        return None

def detect_vehicles(img):
    """Detect vehicles using YOLO model."""
    height, width = img.shape[:2]
    blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(output_layers)

    vehicle_count = 0
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Only count objects with high confidence and class 'car', 'bus', 'truck'
            if confidence > 0.5 and classes[class_id] in ["car", "bus", "truck"]:
                vehicle_count += 1

    print(f"Vehicle count detected: {vehicle_count}")
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

    # Extract the URL of the selected camera
    image_url = selected_camera['Url']

    while True:
        img = fetch_image(image_url)
        if img is not None:
            # Process image and count vehicles
            vehicle_count = detect_vehicles(img)
            save_to_db(vehicle_count, selected_camera)
        
        # Wait before fetching the next image (adjust interval as needed)
        time.sleep(30)

if __name__ == "__main__":
    main()


