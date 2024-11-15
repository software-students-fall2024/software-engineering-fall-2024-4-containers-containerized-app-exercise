from flask import Flask, render_template, Response, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime
import cv2
import requests
import os
import bcrypt
from dotenv import load_dotenv
# pylint: disable=all


# Load environment variables from .env file
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
emotion_data_collection = db["emotion_data"]
users_collection = db["users"]

# Machine Learning Client URL
ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://machine_learning_client:5000")

camera = cv2.VideoCapture(0)  # Initialize camera

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
        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

def detect_emotion(image_data):
    response = requests.post(ML_CLIENT_URL, files={"image": image_data})
    if response.status_code == 200:
        return response.json().get("emotion", "Unknown")
    else:
        return "Error: Unable to detect emotion"

def generate_frames():
    """Generate frames from the camera for video streaming."""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame as part of a multipart HTTP response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def index():
    """Render the home page with the video feed."""
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/capture", methods=["POST"])
def capture():
    """Capture the current frame and detect emotion."""
    if "user_id" not in session:
        flash("Please log in to access this feature.", "error")
        return redirect(url_for("login"))

    success, frame = camera.read()
    if not success:
        flash("Could not capture image from camera.", "error")
        return redirect(url_for("index"))

    # Encode the frame to JPEG format
    _, buffer = cv2.imencode('.jpg', frame)
    image_data = buffer.tobytes()

    # Detect emotion
    emotion_text = detect_emotion(image_data)

    # Save emotion and user information to MongoDB
    emotion_data_collection.insert_one({
        "user_id": session["user_id"],
        "emotion": emotion_text,
        "timestamp": datetime.utcnow()
    })

    flash(f"Emotion detected: {emotion_text}", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    last_emotion = emotion_data_collection.find_one(
        {"user_id": session["user_id"]},
        sort=[("timestamp", -1)]
    )
    return render_template("dashboard.html", last_emotion=last_emotion)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 0)))
    )
