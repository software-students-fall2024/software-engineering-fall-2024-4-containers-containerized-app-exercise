"""
This module contains functions for emotion detection 
using a pre-trained machine learning model.
"""
from datetime import datetime
import cv2
import numpy as np
import tensorflow as tf
from pymongo import MongoClient
import os

# Connect to MongoDB (update the URI with your MongoDB details)
client = MongoClient("mongodb://localhost:27017/")
db = client["emotion_db"]
emotion_data_collection = db["emotion_data"]

# Load the pre-trained emotion detection model
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, 'face_model.h5')  # pylint: disable=no-member

model = tf.keras.models.load_model(model_path) # pylint: disable=no-member

# Define a dictionary to map model output to emotion text
emotion_dict = {
    0: "Happy 😊",
    1: "Sad 😢",
    2: "Angry 😡",
    3: "Surprised 😮",
    4: "Neutral 😐",
}


def detect_emotion(frame):
    """
    Detects emotion from a given frame, saves the result with a timestamp to MongoDB, 
    and returns the detected emotion.

    Args:
        frame (np.array): The image frame captured from the camera.

    Returns:
        str: The detected emotion label.
    """
    # Preprocess the image as required by the model
    resized_frame = cv2.resize(frame, (48, 48))  # Resize to match model input size
    grayscale = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    input_data = np.expand_dims(grayscale, axis=[0, -1]) / 255.0  # Normalize

    # Get the model's prediction
    prediction = model.predict(input_data)
    emotion_label = np.argmax(prediction)
    emotion_text = emotion_dict.get(emotion_label, "Unknown")

    # Save the result to MongoDB with a timestamp
    emotion_data_collection.insert_one(
        {
            "emotion": emotion_text,
            "timestamp": datetime.utcnow(),  # Use UTC time for consistency
        }
    )

    return emotion_text

def run_emotion_detection():
    """
    Opens the camera and runs the emotion detection model in real-time.
    Each frame's detected emotion is displayed and saved to MongoDB.
    """
    cap = cv2.VideoCapture(0)  # Open the default camera (0)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame.")
            break

        # Detect emotion from the current frame
        emotion_text = detect_emotion(frame)

        # Display the emotion text on the frame
        cv2.putText(frame, f"Emotion: {emotion_text}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Show the frame with the detected emotion
        cv2.imshow('Emotion Detection', frame)

        # Press 'q' to quit the video window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_emotion_detection()