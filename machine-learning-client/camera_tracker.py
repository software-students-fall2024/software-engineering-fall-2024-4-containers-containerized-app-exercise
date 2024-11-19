"""
Camera tracking script for monitoring user focus using OpenCV and MongoDB.
"""

import time
from pymongo import MongoClient
import cv2  # pylint: disable=no-name-in-module

# MongoDB connection URI
MONGODB_URI = (
    "mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/"
    "?retryWrites=true&w=majority&appName=itsOver"
)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["itsOver"]
camera_collection = db["camera_activity"]

# Load pre-trained face detector model
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)  # pylint: disable=no-member


def detect_face(frame):
    """Detect faces in the given frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )  # pylint: disable=no-member
    return len(faces) > 0  # Return True if faces are detected


def record_camera_activity(is_focused):
    """Record focus status in MongoDB."""
    timestamp = time.time()  # Current timestamp
    data = {"timestamp": timestamp, "is_focused": is_focused}
    camera_collection.insert_one(data)  # Insert into the collection
    print(f"Recorded: {data}")


def start_camera_tracking():
    """Start tracking user focus using the camera."""
    cap = cv2.VideoCapture(0)  # pylint: disable=no-member

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
            cv2.putText(
                frame,
                feedback,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,  # pylint: disable=no-member
                1,
                (0, 255, 0) if is_focused else (0, 0, 255),
                2,
            )  # pylint: disable=no-member
            cv2.imshow("Camera Tracker", frame)  # pylint: disable=no-member

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):  # pylint: disable=no-member
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()  # pylint: disable=no-member


if __name__ == "__main__":
    start_camera_tracking()
