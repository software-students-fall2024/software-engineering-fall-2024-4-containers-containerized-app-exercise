"""
A simple Flask application.
This module sets up a basic web server using Flask.
"""

import os
import logging
from flask import Flask, render_template, jsonify
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


if __name__ == "__main__":
    # Use Flask configuration from environment variables
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
