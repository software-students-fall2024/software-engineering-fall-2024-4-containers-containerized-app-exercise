"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""
import os # Standard library imports
#from datetime import datetime
from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client['voice_mood_journal']
collection = db['entries']

@app.route('/')
def index():
    """Render the homepage with mood summary data."""
    mood_entries = collection.find().sort("timestamp", -1).limit(100)
    entries = [{
        "file_name": entry["file_name"],
        "transcript": entry["transcript"],
        "sentiment": entry["sentiment"],
        "timestamp": entry["timestamp"]
    } for entry in mood_entries]

    return render_template('index.html', entries=entries)

@app.route('/api/mood-trends')
def mood_trends():
    """Provide mood trend data for visualization."""
    mood_counts = {
        "Positive": collection.count_documents({"sentiment.mood": "Positive"}),
        "Negative": collection.count_documents({"sentiment.mood": "Negative"}),
        "Neutral": collection.count_documents({"sentiment.mood": "Neutral"})
    }
    return jsonify(mood_counts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
