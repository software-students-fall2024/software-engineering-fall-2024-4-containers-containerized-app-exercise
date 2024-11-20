"""
The Machine Learning Client Component of Our Project.
This Module Loads A Trained Machine Learning Model, Preprocesses an Input Image,
Then Classifies the Image as Either Rock, Paper, or Scissors. 
"""

import tensorflow as tf
import numpy as np
from datetime import datetime

MODEL_PATH = "models/rps_model.h5"

# Load the pre-trained model
model = tf.keras.models.load_model(MODEL_PATH)


def classify_image(image_array):
    """
    Classify the user's gesture based on the input image.
    """
    processed_image = preprocess_image(image_array)
    predictions = model.predict(np.expand_dims(processed_image, axis=0))
    classes = ["rock", "paper", "scissors"]
    return classes[np.argmax(predictions)]


def preprocess_image(image):
    """
    Resize and normalize the image for the model.
    """
    image = tf.image.resize(image, (224, 224))  # Match the input size of the model
    image = image / 255.0  # Normalize pixel values
    return image


def store_game_result(games_collection, user_choice, computer_choice, result):
    """
    Store the game details in MongoDB.

    Args:
        games_collection: MongoDB collection instance to store the game data.
        user_choice (str): The user's choice ('rock', 'paper', 'scissors').
        computer_choice (str): The computer's choice.
        result (str): The game result (e.g., 'win', 'lose', 'draw').
    """
    game_data = {
        "timestamp": datetime.now().isoformat(),
        "user_choice": user_choice,
        "computer_choice": computer_choice,
        "result": result,
    }
    games_collection.insert_one(game_data)
    return game_data
