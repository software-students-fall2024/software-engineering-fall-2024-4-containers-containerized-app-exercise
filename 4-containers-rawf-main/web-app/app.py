import random
import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import requests

# Configuration
logging.basicConfig(level=logging.INFO) # logger
logger = logging.getLogger(__name__)

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/") # MongoDB
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "rawf_database")

try:
    client = MongoClient(MONGO_URI)
    DATABASE = client[MONGO_DBNAME]
    logger.info("Connected to MongoDB at %s", MONGO_URI)
except ConnectionFailure as db_error:
    logger.error("Error connecting to MongoDB: %s", db_error)
    DATABASE = None

app = Flask(__name__) # Flask
CORS(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")


# ---------------HTLM FILES---------------
# index.html
@app.route("/")
def home():
    return render_template("index.html")

# tutorial.html
@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")

# game.html
@app.route("/game")
def game():
    return render_template("game.html")

# stats.html
@app.route("/stats")
def stats():
    return render_template("stats.html")


# ---------------MONGODB GAME STATISTICS---------------
"""
# Return sample JSON data
@app.route("/data")
def data():
    sample_data = {
        "name": "Dockerized Flask App",
        "description": "This is a Flask app running inside Docker.",
    }
    return jsonify({"status": "success", "data": sample_data})
"""

# Test MongoDB connection and return database names
@app.route("/test-db")
def test_db():
    try:
        db_list = client.list_database_names()
        logger.info("Successfully retrieved databases: %s", db_list)
        return jsonify({"status": "success", "databases": db_list})
    except ConnectionFailure as db_conn_error: # Renamed variable
        logger.error("Error retrieving databases: %s", db_conn_error)
        return jsonify({"status": "error", "message": str(db_conn_error)}), 500

""""
# Add data to database NEED TO IMPLEMENT!!!
@app.route("/add_data", methods=["POST"])
def add_data():
    try:
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as add_data_exception:  # pylint: disable=broad-except
        logger.error("Error adding data: %s", add_data_exception)
        return jsonify({"message": f"Error adding data: {add_data_exception}"}), 500
"""

# Generate computer choice
def random_computer_choice():
    choices = ["Rock", "Paper", "Scissors"]
    return random.choice(choices)


# Determine result of game
def determine_winner(user_choice, comp_choice):
    # tie
    if user_choice == comp_choice: return "Nobody"
    
    # user wins
    elif (user_choice == "Rock" and comp_choice == "Scissors") or \
        (user_choice == "Paper" and comp_choice == "Rock") or \
        (user_choice == "Scissors" and comp_choice == "Paper"):
        return "User"
    
    # computer wins
    else: return "Computer"


# Route results to game.html
@app.route("/", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        user_choice = request.form.get("user_choice")  # User's choice from the frontend
        computer_choice = random_computer_choice()
        winner = determine_winner(user_choice, computer_choice)
        return render_template(
            "game.html",
            user_choice=user_choice,
            computer_choice=computer_choice,
            winner=winner,
        )
    return render_template("game.html", user_choice="", computer_choice="", winner="")


# ---------------ML CLIENT---------------
ML_CLIENT_URL = "http://ml-client:5001"  # Machine Learning Client's API endpoint


"""
# Classify image using ML Client
@app.route("/classify", methods=["POST"])
def classify():
    try:
        # Capture the uploaded image and preprocess it
        image = requests.files["image"]  # pylint: disable=no-member

        # Send the image to the ML Client API for preprocessing
        preprocess_response = requests.post(
            f"{ML_CLIENT_URL}/preprocess", files={"image": image}, timeout=10
        )
        if preprocess_response.status_code != 200:
            return jsonify({"status": "error", "message": "Preprocessing failed"}), 500

        # Receive the preprocessed image array
        image_array = preprocess_response.json().get("image_array")
        if not image_array:
            return (
                jsonify(
                    {"status": "error", "message": "Invalid preprocessing response"}
                ),
                500,
            )

        # Send the image_array to the ML Client API
        response = requests.post(
            f"{ML_CLIENT_URL}/classify",
            json={"image_array": image_array.tolist()},
            timeout=10,
        )
        response_data = response.json()
        if "error" in response_data:
            return jsonify({"status": "error", "message": response_data["error"]}), 500

        user_choice = response_data["result"]

        # Simulate computer choice
        computer_choice = random_computer_choice()

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
            timeout=10,
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
"""

if __name__ == "__main__":
    # Use Flask configuration from environment variables
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )