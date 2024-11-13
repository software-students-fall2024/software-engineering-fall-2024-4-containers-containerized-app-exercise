import uuid
from datetime import datetime
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import nltk
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
# Download NLTK data for sentence tokenization

nltk.download("punkt")

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  # Adjust the connection string if necessary
db = client["sentiment"]  # Database name
collection = db["texts"]  # Collection name


mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  # Adjust the connection string if necessary
db = client["sentiment"]  # Database name
collection = db["texts"]  # Collection name


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/checkSentiment", methods=["POST"])
def submit_sentence():
    data = request.get_json()
    paragraph = data.get("sentence")

    # Split paragraph into individual sentences
    sentences = sent_tokenize(paragraph)

    # Generate a unique request_id
    request_id = str(uuid.uuid4())

    # Create sentence entries with status "pending" and analysis as null
    sentence_entries = [
        {"sentence": sentence, "status": "pending", "analysis": None}
        for sentence in sentences
    ]

    # Create the document structure
    document = {
        "request_id": request_id,
        "sentences": sentence_entries,
        "overall_status": "pending",
        "timestamp": datetime.now(),
    }

    # Insert into MongoDB
    collection.insert_one(document)

    # Return the request_id for fetching results later
    return jsonify({"request_id": request_id})


@app.route("/get_analysis", methods=["GET"])
def get_analysis():
    request_id = request.args.get("request_id")
    document = collection.find_one(
        {"request_id": request_id, "overall_status": "processed"}
    )
    if document:
        return jsonify(document)
    else:
        return jsonify({"message": "No processed analysis found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
