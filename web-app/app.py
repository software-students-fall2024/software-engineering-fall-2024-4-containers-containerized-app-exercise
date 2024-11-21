"""
Flask application with camera and mouse tracking integration using OpenCV and MongoDB.
"""

import os
import math
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
)
import pymongo
import certifi
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# MongoDB connection
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = mongo_client[os.getenv("MONGO_DBNAME")]

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Focus threshold
FOCUS_THRESHOLD = 5  # Time in seconds


# Mouse tracking metrics class
class MouseMetrics:
    def __init__(self):
        self.mouse_distance = 0
        self.click_count = 0
        self.last_x = None
        self.last_y = None
        self.focused_time = 0
        self.unfocused_time = 0
        self.is_focused = True
        self.last_event_time = time.time()

    def process_mouse_move(self, x, y):
        current_time = time.time()
        time_since_last_event = current_time - self.last_event_time
        self.last_event_time = current_time

        # Calculate distance moved
        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            self.mouse_distance += distance
        self.last_x, self.last_y = x, y

        # Update focus state
        if time_since_last_event > FOCUS_THRESHOLD:
            self.unfocused_time += time_since_last_event - FOCUS_THRESHOLD
            self.is_focused = False
        else:
            self.focused_time += time_since_last_event
            self.is_focused = True

    def process_mouse_click(self):
        self.click_count += 1

    def generate_report(self):
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (
            (self.focused_time / total_time) * 100 if total_time > 0 else 0
        )
        return {
            "total_mouse_distance": round(self.mouse_distance, 2),
            "total_clicks": self.click_count,
            "focused_time": round(self.focused_time, 2),
            "unfocused_time": round(self.unfocused_time, 2),
            "focus_percentage": round(focus_percentage, 2),
            "overall_status": "Focused" if focus_percentage > 50 else "Unfocused",
        }


# Initialize mouse metrics
mouse_metrics = MouseMetrics()

# Test MongoDB connection
try:
    mongo_client.admin.command("ping")
    print(" * Connected to MongoDB!")
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f" * MongoDB connection error: {e}")


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data["_id"]))
    return None


@app.route("/", methods=["GET", "POST"])
def login():
    """
    Route for the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_data = db.users.find_one({"username": username})

        if user_data and user_data["password"] == password:
            user = User(str(user_data["_id"]))
            login_user(user)
            return redirect(url_for("home_page"))
        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Route for the sign-up page.
    Allows new users to create an account and saves their information to the database.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for("signup"))

        new_user = {"username": username, "password": password}
        db.users.insert_one(new_user)

        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/home_page")
@login_required
def home_page():
    """
    Route for the home page.

    Returns:
        str: The rendered HTML template.
    """
    past_sessions = db.sessions.find({"username": current_user.id}).sort(
        "created_at", -1
    )
    return render_template(
        "home_page.html", past=past_sessions, username=current_user.id
    )


@app.route("/start-session")
def session_form():
    """
    Render the focus session control page.
    """
    return render_template("focus.html")


@app.route("/track-mouse", methods=["POST"])
def track_mouse():
    try:
        data = request.json
        event = data.get("event")
        x, y = data.get("x"), data.get("y")

        if event == "mousemove":
            mouse_metrics.process_mouse_move(x, y)
        elif event == "click":
            mouse_metrics.process_mouse_click()

        # db.mouse_activity.insert_one({**data, "timestamp": time.time()})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/mouse-report", methods=["GET"])
def mouse_report():
    try:
        # Generate the sanitized report
        report = mouse_metrics.generate_report()

        # Add a timestamp to the report
        report["timestamp"] = time.time()

        # Insert the report into the database
        insert_result = db.mouse_activity.insert_one(report)

        # Add the MongoDB ObjectId to the report (as a string for JSON compatibility)
        report["_id"] = str(insert_result.inserted_id)

        # Return the report as a JSON response
        return jsonify(report), 200
    except Exception as e:
        # Log and return an error if something goes wrong
        print(f"Error inserting mouse report: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/start-camera", methods=["POST"])
def start_camera():
    try:
        # Placeholder for actual camera tracking logic
        return jsonify({"status": "Camera started"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/stop-camera", methods=["POST"])
def stop_camera():
    try:
        # Placeholder for actual camera tracking logic
        return jsonify({"status": "Camera stopped"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(port=os.getenv("FLASK_PORT", 5000), debug=True)
