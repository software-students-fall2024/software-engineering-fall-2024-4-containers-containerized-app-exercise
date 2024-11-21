"""
A simple Flask application.
This module sets up a basic web server using Flask.
"""

import random
import os
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import requests


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "rawf_database")

try:
    client = MongoClient(MONGO_URI)
    DATABASE = client[MONGO_DBNAME]
    logger.info("Connected to MongoDB at %s", MONGO_URI)
except ConnectionFailure as db_error:
    logger.error("Error connecting to MongoDB: %s", db_error)
    DATABASE = None

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Secret key configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")


@app.route("/")
def home():
    """Render the index page."""
    return render_template("index.html")


@app.route("/tutorial")
def tutorial():
    """Render the tutorial page."""
    return render_template("tutorial.html")


@app.route("/game")
def game():
    """Render the game page."""
    return render_template("game.html")


@app.route("/stats")
def stats():
    """Render the stats page."""
    return render_template("stats.html")


@app.route("/data")
def data():
    """Return sample JSON data."""
    sample_data = {
        "name": "Dockerized Flask App",
        "description": "This is a Flask app running inside Docker.",
    }
    return jsonify({"status": "success", "data": sample_data})


@app.route("/test-db")
def test_db():
    """Test MongoDB connection and return database names."""
    try:
        db_list = client.list_database_names()
        logger.info("Successfully retrieved databases: %s", db_list)
        return jsonify({"status": "success", "databases": db_list})
    except ConnectionFailure as db_conn_error:  # Renamed variable
        logger.error("Error retrieving databases: %s", db_conn_error)
        return jsonify({"status": "error", "message": str(db_conn_error)}), 500


@app.route("/add_data", methods=["POST"])
def add_data():
    """
    Add data to the database.
    Currently, this function is not implemented and will raise a NotImplementedError.
    """
    try:
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as add_data_exception:  # pylint: disable=broad-except
        logger.error("Error adding data: %s", add_data_exception)
        return jsonify({"message": f"Error adding data: {add_data_exception}"}), 500


def simulate_computer_choice():
    """
    Simulate the computer's choice for the game.
    Randomly chooses between 'rock', 'paper', and 'scissors'.
    """
    choices = ["rock", "paper", "scissors"]
    return random.choice(choices)


def determine_result(user_choice, computer_choice):
    """
    Determine the result of the game based on user and computer choices.

    Args:
        user_choice (str): The user's choice ('rock', 'paper', or 'scissors').
        computer_choice (str): The computer's choice ('rock', 'paper', or 'scissors').

    Returns:
        str: The result of the game ('win', 'lose', or 'draw').
    """
    # Case when both the user and computer choose the same option
    if user_choice == computer_choice:
        return "draw"

    # Rules: rock beats scissors, scissors beat paper, paper beats rock
    win_conditions = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock",
    }

    # If the computer's choice is what the user's choice beats, the user wins
    if win_conditions[user_choice] == computer_choice:
        return "win"

    # Otherwise, the user loses
    return "lose"


ML_CLIENT_URL = "http://ml-client:5001"  # Machine Learning Client's API endpoint


@app.route("/classify", methods=["POST"])
def classify():
    """
    Route to classify an image using the machine learning client.
    """
    try:
        # Capture the uploaded image and preprocess it
        image = requests.files["image"]
        image_array = preprocess_uploaded_image(image)  # Convert image to numpy array

        # Send the image_array to the ML Client API
        response = requests.post(
            f"{ML_CLIENT_URL}/classify", json={"image_array": image_array.tolist()}
        )
        response_data = response.json()
        if "error" in response_data:
            return jsonify({"status": "error", "message": response_data["error"]}), 500

        user_choice = response_data["result"]

        # Simulate computer choice
        computer_choice = simulate_computer_choice()

        # Determine the result of the game
        result = determine_result(user_choice, computer_choice)

        # Store the game result via the ML Client API
        store_response = requests.post(
            f"{ML_CLIENT_URL}/store",
            json={
                "user_choice": user_choice,
                "computer_choice": computer_choice,
                "result": result,
            },
        )
        if store_response.status_code != 200:
            return (
                jsonify({"status": "error", "message": "Failed to store game result"}),
                500,
            )

        return jsonify(
            {
                "user_choice": user_choice,
                "computer_choice": computer_choice,
                "result": result,
            }
        )
    except Exception as e:  # pylint: disable=broad-except
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Use Flask configuration from environment variables
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
