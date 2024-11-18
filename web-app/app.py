"""
A Flask web application for a Rock-Paper-Scissors game with AI and ML integration.
"""

import os
import time
import random
<<<<<<< HEAD
import logging  # Fixed import order
from flask import Flask, render_template, request, jsonify, make_response
=======
import logging
from flask import Flask, render_template, request, jsonify
>>>>>>> a1d69f762ec00dda2f9165eac1c7fe5402402f22
import requests
from requests.exceptions import RequestException
from pymongo import MongoClient
from bson import ObjectId

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
client = MongoClient(MONGO_URI)
db = client["rps_database"]
collection = db["stats"]


def generate_stats_doc():
    """
    Creates blank stats-tracking document.

    Returns:
        _id (str): ObjectId for newly created document
    """

    stats = {
        "Rock": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Paper": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Scissors": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Totals": {"wins": 0, "losses": 0, "ties": 0},
    }
    _id = str(collection.insert_one(stats).inserted_id)
    return _id


def retry_request(url, files, retries=5, delay=2, timeout=10):
    """
    Retry a POST request multiple times with a delay on failure.

    Args:
        url (str): URL to send the request to.
        files (dict): Files to send in the POST request.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.
        timeout (int): Timeout for the request in seconds.

    Returns:
        Response: Response object from the successful POST request, or None if all retries fail.
    """
    for attempt in range(retries):
        try:
            response = requests.post(url, files=files, timeout=timeout)
            response.raise_for_status()
            return response
        except RequestException as error:
            logging.warning("Retry attempt %d failed: %s", attempt + 1, str(error))
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error("All retry attempts failed.")
                return None
    return None


@app.route("/")
def home():
    """Render the home page."""
    resp = make_response(render_template("title.html"))
    if "db_object_id" not in request.cookies:
        resp.set_cookie("db_object_id", generate_stats_doc())
    return resp


@app.route("/index")
def index():
    """Render the index page."""
    resp = make_response(render_template("index.html"))
    if "db_object_id" not in request.cookies:
        resp.set_cookie("db_object_id", generate_stats_doc())
    return resp


@app.route("/statistics")
def statistics():
    """Render the statistics page."""
    _id = request.cookies.get("db_object_id", default=None)
    if not _id:
        _id = generate_stats_doc()
    stats = collection.find_one({"_id": ObjectId(_id)}, {"_id": 0})
    resp = make_response(render_template("statistics.html", stats_data=stats))
    resp.set_cookie("db_object_id", _id)
    return resp


@app.route("/result", methods=["POST"])
def result():
    """
    Handle the result of the Rock-Paper-Scissors game.

    Accepts an image from the user, sends it to the machine learning client
    for gesture prediction, and returns the game result.
    """
    app.logger.debug("Received request at /result")
    try:
        if "image" not in request.files:
            app.logger.error("No image file provided")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        ml_client_url = os.getenv(
            "ML_CLIENT_URL", "http://machine-learning-client:5000"
        )
        app.logger.debug("Sending image to ML client at %s/predict", ml_client_url)
        response = retry_request(f"{ml_client_url}/predict", files={"image": file})
        if not response:
            app.logger.error("ML client did not respond")
            return render_template(
                "result.html",
                user="Unknown",
                ai=random.choice(["Rock", "Paper", "Scissors"]),
                result="No valid prediction. Please try again.",
            )
        user_gesture = response.json().get("gesture", "Unknown")
        if user_gesture == "Unknown":
            app.logger.warning("Prediction returned 'Unknown'.")
            return render_template(
                "result.html",
                user="Unknown",
                ai=random.choice(["Rock", "Paper", "Scissors"]),
                result="Gesture not recognized. Please try again.",
            )
    except RequestException as error:
        app.logger.error("Error communicating with ML client: %s", str(error))
        return jsonify({"error": "Error communicating with ML client"}), 500

    ai_gesture = random.choice(["Rock", "Paper", "Scissors"])
    game_result = determine_winner(user_gesture, ai_gesture)
    app.logger.debug("Game result: %s", game_result)
    _id = request.cookies.get("db_object_id")
    if game_result == "AI wins!":
        res = "losses"
    elif game_result == "It's a tie!":
        res = "ties"
    else:
        res = "wins"
    collection.update_one(
        {"_id": ObjectId(_id)},
        {
            "$inc": {
                "Totals" + "." + res: 1,
                user_gesture + "." + res: 1,
                user_gesture + "." + "total": 1,
            }
        },
        upsert=False,
    )
    return render_template(
        "result.html", user=user_gesture, ai=ai_gesture, result=game_result
    )


def determine_winner(user, ai_choice):
    """
    Determine the winner of the Rock-Paper-Scissors game.

    Args:
        user (str): User's gesture.
        ai_choice (str): AI's gesture.

    Returns:
        str: Result of the game.
    """
    winning_cases = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper",
    }
    if user == ai_choice:
        return "It's a tie!"
    if ai_choice == winning_cases.get(user):
        return "You win!"
    return "AI wins!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
