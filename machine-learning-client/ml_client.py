"""
The Machine Learning Client Component of Our Project.
This Module Loads A Trained Machine Learning Model, Preprocesses an Input Image,
Then Classifies the Image as Either Rock, Paper, or Scissors. 
"""

# pylint: disable=no-name-in-module

from datetime import datetime
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

MODEL_PATH = "models/rps_model.h5"

# Load the pre-trained model
model = tf.keras.models.load_model(MODEL_PATH)

# Initialize Flask app
app = Flask(__name__)

@app.route("/classify", methods=["POST"])
def classify():
    """
    API endpoint to classify an image.
    Expects a JSON request with the key "image_array".
    """
    try:
        # Get the image array from the JSON body
        image_array = np.array(request.json.get("image_array"))
        if image_array is None:
            return jsonify({"error": "No image_array provided"}), 400

        # Classify the image
        processed_image = preprocess_image(image_array)
        predictions = model.predict(np.expand_dims(processed_image, axis=0))
        classes = ["rock", "paper", "scissors"]
        result = classes[np.argmax(predictions)]

        return jsonify({"result": result})
    except Exception as e:  # pylint: disable=broad-except
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/store", methods=["POST"])
def store():
    """
    API endpoint to store game results.
    Expects JSON request with keys "user_choice", "computer_choice", and "result".
    """
    try:
        # Extract data from the JSON body
        data = request.json
        user_choice = data.get("user_choice")
        computer_choice = data.get("computer_choice")
        result = data.get("result")

        if not all([user_choice, computer_choice, result]):
            return jsonify({"error": "Missing required fields"}), 400

        # Here, you could implement MongoDB storage if needed
        # For now, we mock the storage response
        stored_data = {
            "timestamp": datetime.now().isoformat(),
            "user_choice": user_choice,
            "computer_choice": computer_choice,
            "result": result,
        }

        return jsonify({"status": "success", "data": stored_data})
    except Exception as e:  # pylint: disable=broad-except
        return jsonify({"error": str(e)}), 500


def preprocess_image(image):
    """
    Resize and normalize the image for the model.
    """
    image = tf.image.resize(image, (224, 224))  # Match the input size of the model
    image = image / 255.0  # Normalize pixel values
    return image


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
