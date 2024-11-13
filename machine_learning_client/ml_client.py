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
    4: "Neutral 😐",  # Update based on your model's classes
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
