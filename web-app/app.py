"""
A simple Flask application.
This module sets up a basic web server using Flask.
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

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
    db = client[MONGO_DBNAME]
    logger.info("Connected to MongoDB at %s", MONGO_URI)
except ConnectionFailure as db_error:
    logger.error("Error connecting to MongoDB: %s", db_error)
    db = None

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

@app.route('/stats')
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


if __name__ == "__main__":
    # Use Flask configuration from environment variables
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1"
    )