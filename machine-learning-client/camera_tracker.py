import cv2
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
MONGODB_URI = "mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority&appName=itsOver"


# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["itsOver"]
camera_collection = db["camera_activity"]

# Load pre-trained face detector model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_face(frame):
    """Detect faces in the given frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces) > 0  # Return True if faces are detected

def record_camera_activity(is_focused):
    """Record focus status in MongoDB."""
    import time
    timestamp = time.time()  # Current timestamp
    data = {"timestamp": timestamp, "is_focused": is_focused}
    camera_collection.insert_one(data)  # Insert into the collection
    print(f"Recorded: {data}")

def start_camera_tracking():
    """Start tracking user focus using the camera."""
    cap = cv2.VideoCapture(0)  # Open the default camera

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # Detect face and determine focus
            is_focused = detect_face(frame)
            record_camera_activity(is_focused)

            # Display the frame with feedback
            feedback = "Focused" if is_focused else "Not Focused"
            cv2.putText(frame, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if is_focused else (0, 0, 255), 2)
            cv2.imshow("Camera Tracker", frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    start_camera_tracking()