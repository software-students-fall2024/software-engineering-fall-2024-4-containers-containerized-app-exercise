from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime
import cv2
import requests
import os
import bcrypt
from dotenv import load_dotenv
# pylint: disable=all

# Load environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
emotion_data_collection = db["emotion_data"]
users_collection = db["users"]

# ML Client URL (from environment variables)
ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://machine_learning_client:5000/detect_emotion")

# Camera initialization
camera = cv2.VideoCapture(0)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password"]):
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session.permanent = False
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


def generate_frames():
    """Generate frames from the camera for video streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/")
def index():
    """Render welcome page."""
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/capture", methods=["POST"])
def capture():
    """Capture the current frame and detect emotion using ml_client."""
    if "user_id" not in session:
        return {"error": "Please log in to access this feature."}, 401

    success, frame = camera.read()
    if not success:
        return {"error": "Could not capture image from camera."}, 500

    _, buffer = cv2.imencode(".jpg", frame)
    image_data = buffer.tobytes()

    try:
        response = requests.post(
            ML_CLIENT_URL, files={"image": ("frame.jpg", image_data, "image/jpeg")}
        )
        response.raise_for_status()
        emotion_text = response.json().get("emotion", "Unknown")
    except requests.RequestException as e:
        return {"error": f"Unable to detect emotion: {str(e)}"}, 500

    timestamp = datetime.now(datetime.timezone.utc).isoformat()
    emotion_data_collection.insert_one(
        {
            "user_id": session["user_id"],
            "emotion": emotion_text,
            "timestamp": timestamp,
        }
    )

    return {"emotion": emotion_text, "timestamp": timestamp}

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    last_emotion = emotion_data_collection.find_one(
        {"user_id": session["user_id"]}, sort=[("timestamp", -1)]
    )
    username = session.get("username", "User")
    return render_template("dashboard.html", last_emotion=last_emotion, username=username)


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 0))),
    )