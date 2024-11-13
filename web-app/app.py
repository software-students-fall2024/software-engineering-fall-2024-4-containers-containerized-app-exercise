import uuid
from datetime import datetime
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  # Adjust the connection string if necessary
db = client["sentiment"]  # Database name
collection = db["texts"]  # Collection name

@app.route("/")
def index():
    """Render the main index page."""
    return render_template("index.html")

@app.route("/checkSentiment", methods=["POST"])
def submit_sentence():
    """Handle sentiment check requests and store the sentence in MongoDB."""
    data = request.get_json()
    sentence = data.get("sentence")

    # Generate a unique request_id
    request_id = str(uuid.uuid4())

    # Create the data structure with status "pending" and analysis as null
    document = {
        "request_id": request_id,
        "sentences": [{"sentence": sentence, "status": "pending", "analysis": None}],
        "overall_status": "pending",
        "timestamp": datetime.now()
    }

    # Insert into MongoDB
    collection.insert_one(document)

    # Return the user's input sentence
    return jsonify({'request_id': request_id, 'analysis': sentence})

@app.route("/get_analysis", methods=["GET"])
def get_analysis():
    request_id = request.args.get("request_id")
    document = collection.find_one({"request_id": request_id, "overall_status": "processed"})
    if document:
        return jsonify(document)
    else:
        return jsonify({"message": "No processed analysis found"}), 404

if __name__ == "__main__":
    app.run(debug=True)