"""
Flask application with camera and mouse tracking integration using OpenCV and MongoDB.
"""

import os
import math
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
    logout_user,
)
import pymongo
import certifi
from bson.objectid import ObjectId
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# MongoDB connection
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = mongo_client[os.getenv("MONGO_DBNAME")]

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Constants
FOCUS_THRESHOLD = 5  # Time in seconds


class MouseMetrics:
    """
    A class to handle and process mouse tracking metrics.
    """

    def __init__(self):
        self.mouse_distance = 0
        self.click_count = 0
        self.focused_time = 0
        self.unfocused_time = 0
        self.last_x = None
        self.last_y = None
        self.last_event_time = time.time()

    def process_mouse_move(self, x, y):
        """
        Process mouse movement and calculate distance moved.
        """
        current_time = time.time()
        time_since_last_event = current_time - self.last_event_time

        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            self.mouse_distance += distance

        self.last_x, self.last_y = x, y

        # Update focus state
        if time_since_last_event > FOCUS_THRESHOLD:
            self.unfocused_time += time_since_last_event - FOCUS_THRESHOLD
        else:
            self.focused_time += time_since_last_event

        self.last_event_time = current_time

    def process_mouse_click(self):
        """
        Increment the click count when a mouse click event is detected.
        """
        self.click_count += 1

    def generate_report(self):
        """
        Generate a report with the collected mouse metrics.
        """
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


mouse_metrics = MouseMetrics()


class User(UserMixin):
    """
    Flask-Login User class to manage user sessions.
    """

    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user object by ID.
    """
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data["_id"]))
    return None


@app.template_filter("datetimeformat")
def datetimeformat(value, fmt="%B %d, %Y, %I:%M %p"):
    """
    Custom Jinja2 filter to format Unix timestamps into human-readable dates.
    """
    return datetime.fromtimestamp(value).strftime(fmt)


@app.route("/", methods=["GET", "POST"])
def login():
    """
    Route for user login.
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
    Route for user sign-up.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please log in.")
            return redirect(url_for("login"))

        db.users.insert_one({"username": username, "password": password})
        flash("Account created successfully. Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/home_page")
@login_required
def home_page():
    """
    Display the logged-in user's past sessions.
    """
    user_sessions = list(
        db.mouse_activity.find({"user_id": current_user.id}).sort("timestamp", -1)
    )
    for session in user_sessions:
        session["_id"] = str(session["_id"])  # Convert ObjectId to string for rendering
    return render_template("home_page.html", past_sessions=user_sessions)


@app.route("/start-session")
@login_required
def session_form():
    """
    Render the session control page.
    """
    return render_template("focus.html")


@app.route("/track-mouse", methods=["POST"])
def track_mouse():
    """
    Track mouse movement and clicks.
    """
    data = request.json
    event = data.get("event")
    x, y = data.get("x"), data.get("y")

    if event == "mousemove":
        mouse_metrics.process_mouse_move(x, y)
    elif event == "click":
        mouse_metrics.process_mouse_click()

    return jsonify({"status": "success"}), 200


@app.route("/mouse-report", methods=["GET"])
@login_required
def mouse_report():
    """
    Generate and store the mouse tracking report.
    """
    report = mouse_metrics.generate_report()
    report["timestamp"] = time.time()
    report["user_id"] = current_user.id

    insert_result = db.mouse_activity.insert_one(report)
    report["_id"] = str(insert_result.inserted_id)

    return jsonify(report), 200


@app.route("/logout")
@login_required
def logout():
    """
    Logout the current user and redirect to login page.
    """
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
