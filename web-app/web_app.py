"""
This is a web app module for Attendify
"""

import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["test_db"]
users_collection = db["users"]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

print(os.urandom(24).hex())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
