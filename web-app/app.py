"""
This application serves as the main entry point for the Flask web application,
connecting to MongoDB and providing the frontend interface.
"""

from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["object_detection"]
collection = db["detected_objects"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    """Fetch data from MongoDB"""
    data = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB IDs
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
