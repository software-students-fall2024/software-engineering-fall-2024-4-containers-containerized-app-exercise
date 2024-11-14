"""
A Flask web application for a Rock-Paper-Scissors game with AI and ML integration.
"""

import os
import time
import random
from flask import Flask, render_template, request
import requests
from requests.exceptions import RequestException

app = Flask(__name__)

def retry_request(url, files, retries=5, delay=2):
    """
    Retry a POST request multiple times with a delay on failure.

    Args:
        url (str): URL to send the request to.
        files (dict): Files to send in the POST request.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        Response: Response object from the successful POST request, or None if all retries fail.
    """
    for attempt in range(retries):
        try:
            response = requests.post(url, files=files)
            response.raise_for_status()
            return response
        except RequestException as exception:
            if attempt < retries - 1:
                time.sleep(delay)
    return None

@app.route("/")
def home():
    """Render the home page."""
    return render_template("title.html")

@app.route("/index")
def index():
    """Render the index page."""
    return render_template("index.html")

@app.route("/statistics")
def statistics():
    """Render the statistics page."""
    return render_template("statistics.html")

@app.route("/result", methods=["POST"])
def result():
    """
    Handle user input, send it to the ML client, and determine the result of the game.

    Returns:
        Rendered result page with user and AI gestures and the game result.
    """
    try:
        file = request.files["image"]
        ml_client_url = os.getenv("ML_CLIENT_URL", "http://machine-learning-client:5000")
        response = retry_request(f"{ml_client_url}/predict", files={"image": file})
        if not response:
            return "Error: ML client did not respond."
        user_gesture = response.json().get("gesture", "Unknown")
    except RequestException as exception:
        return f"Error communicating with ML client: {str(exception)}"
    ai_gesture = random.choice(["Rock", "Paper", "Scissors"])
    game_result = determine_winner(user_gesture, ai_gesture)
    return render_template("result.html", user=user_gesture, ai=ai_gesture, result=game_result)

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
    