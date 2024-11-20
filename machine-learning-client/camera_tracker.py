"""
Camera tracking script for monitoring user focus using OpenCV and MongoDB.
"""

import time
from pymongo import MongoClient
import cv2  # pylint: disable=no-name-in-module
from threading import Thread, Event

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

# Stop event to signal termination
stop_event = Event()


def detect_face(frame):
    """Detect faces in the given frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # pylint: disable=no-member
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )  # pylint: disable=no-member
    return len(faces) > 0  # Return True if faces are detected


def record_summary(total_time, focused_time):
    """Record a summary of tracking in MongoDB."""
    focus_percentage = (focused_time / total_time) * 100 if total_time > 0 else 0
    data = {
        "timestamp": time.time(),  # Record time
        "total_time": round(total_time, 2),
        "focused_time": round(focused_time, 2),
        "focus_percentage": round(focus_percentage, 2),
    }
    camera_collection.insert_one(data)  # Insert into the collection
    print(f"Recorded summary: {data}")


def _camera_tracking():
    """Internal function for running the camera tracker."""
    cap = cv2.VideoCapture(0)  # pylint: disable=no-member

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    total_time = 0
    focused_time = 0
    start_time = time.time()  # Tracking start time

    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # Detect face and determine focus
            is_focused = detect_face(frame)

            # Increment total and focused time
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            if is_focused:
                focused_time += elapsed_time

            # Reset start time for next loop
            start_time = time.time()

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

            # Stop tracking after 10 seconds
            if total_time >= 10:
                record_summary(total_time, focused_time)
                stop_event.set()

            # Small delay to process frames
            cv2.waitKey(1)  # pylint: disable=no-member
    finally:
        cap.release()
        cv2.destroyAllWindows()  # pylint: disable=no-member


def start_tracking():
    """Start the camera tracking."""
    global stop_event
    stop_event.clear()
    tracker_thread = Thread(target=_camera_tracking, daemon=True)
    tracker_thread.start()
    print("Camera tracking started.")


def stop_tracking():
    """Stop the camera tracking."""
    global stop_event
    stop_event.set()
    print("Camera tracking stopped.")


if __name__ == "__main__":
    print("Testing local tracking. Start tracking for 10 seconds...")
    start_tracking()
    time.sleep(12)  # Allow tracking to run for 10 seconds
    stop_tracking()
