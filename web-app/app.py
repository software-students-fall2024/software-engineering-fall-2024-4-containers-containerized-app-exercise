"""
This is the main application file for the Swear Jar app.

It uses Flask to serve an HTML template and a REST API for swear counts.
Data is stored in a MongoDB database.
"""
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["swearDB"]
swears_collection = db["swears"]

@app.route("/")
def index():
    """
    Render the homepage with the total number of swears.
    """
    total_swears = sum(doc["count"] for doc in swears_collection.find())
    return render_template("index.html", swears=total_swears)

@app.route("/api/swears", methods=["GET"])
def get_swear_counts():
    """
    Return the swear counts
    """
    docs = swears_collection.find()
    for doc in docs:
        print(doc)
    swear_counts = {doc["word"]: doc["count"] for doc in swears_collection.find()}
    return jsonify(swear_counts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
