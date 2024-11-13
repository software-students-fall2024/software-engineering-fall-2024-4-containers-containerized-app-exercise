"""
This is a web app module for Attendify
"""

import os
from flask import Flask, jsonify
from pymongo import MongoClient


app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["test_db"]


@app.route("/")
def home():
    """Handles the home route."""
    return "Welcome to the Web App!"


@app.route("/test-insert")
def test_insert():
    """Insert a test document into MongoDB and return the inserted ID."""
    collection = db["test_collection"]

    # Create a sample document to insert
    sample_data = {"name": "Test", "email": "test@nyu.edu", "age": 21}

    result = collection.insert_one(sample_data)

    return jsonify({"status": "success", "inserted_id": str(result.inserted_id)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
