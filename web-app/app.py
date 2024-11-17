"""
A simple Flask application.
This module sets up a basic web server using Flask.
""" 
import os
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "rawf_database")  # Default to 'rawf_database'
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DBNAME]
    logger.info(f"Connected to MongoDB at {MONGO_URI}")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    db = None

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Secret key configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Define a route for the homepage
@app.route("/")
def home():
    """Returns the index.html file."""
    return render_template("index.html")

# Define a route for the tutorial page
@app.route("/tutorial")
def tutorial():
    """Returns the tutorial.html file."""
    return render_template("tutorial.html")

# Define a route for the game page
@app.route("/game")
def game():
    """Returns the game.html file."""
    return render_template("game.html")

@app.route('/stats')
def stats():
    return render_template("stats.html")
# Define a route for JSON data
@app.route("/data")
def data():
    """Returns a JSON of the data."""
    sample_data = {
        "name": "Dockerized Flask App",
        "description": "This is a Flask app running inside Docker.",
    }
    return jsonify({"status": "success", "data": sample_data})

# Test MongoDB connection
@app.route("/test-db")
def test_db():
    """Test MongoDB connection and return database names."""
    try:
        db_list = client.list_database_names()
        logger.info("Successfully retrieved databases: %s", db_list)
        return jsonify({"status": "success", "databases": db_list})
    except Exception as e:
        logger.error(f"Error retrieving databases: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Run the app only if this file is executed directly
if __name__ == "__main__":
    # Use Flask configuration from environment variables
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "1") == "1"
    )