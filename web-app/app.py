"""
Web application for sound classification.

This Flask app provides a web interface for recording audio and displaying classification results.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)

# MongoDB connection settings
MONGO_HOST = os.environ.get("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = "sound_classification"
MONGO_COLLECTION = "results"

# Initialize MongoDB client
client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


@app.route("/")
def home():
    """Render the home page."""
    return render_template("home.html")


@app.route("/analyze")
def analyze():
    """Render the analyze sound page."""
    return render_template("analyze.html")


@app.route("/save_result", methods=["POST"])
def save_result():
    """Save classification result to MongoDB."""
    data = request.get_json()
    if data:
        collection.insert_one(
            {
                "classification": data.get("classification"),
                "timestamp": data.get("timestamp"),
            }
        )
        return {"status": "success"}, 200
    return {"status": "error", "message": "No data received"}, 400


@app.route("/results")
def results():
    """Retrieve and display stored classification results."""
    classification_results = list(collection.find())
    return render_template("results.html", results=classification_results)


@app.route("/delete_result/<result_id>", methods=["POST"])
def delete_result(result_id):
    """Delete a result from MongoDB."""
    collection.delete_one({"_id": ObjectId(result_id)})
    return redirect(url_for("results"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
