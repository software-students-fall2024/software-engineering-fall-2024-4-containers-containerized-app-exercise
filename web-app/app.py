from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime
import cv2
import sys
import requests
import os
from werkzeug.security import generate_password_hash, check_password_hash

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, project_root)

sys.path.append('')

app = Flask(__name__)

ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://machine_learning_client:5000")

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["emotion_db"]
emotion_data_collection = db["emotion_data"]

def detect_emotion(image_data):
    response = requests.post("http://machine_learning_client:5000/detect_emotion", files={"image": image_data})
    if response.status_code == 200:
        return response.json()["emotion"]
    else:
        return "Error: Unable to detect emotion"
    

@app.route('/process_emotion', methods=['POST'])
def process_emotion():
    # Call the detect_emotion function without needing an image path
    result = detect_emotion()
    
    return jsonify(result)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        image = request.files.get("image")
        if not image:
            return "No image provided", 400

        # Send the image to the machine learning client
        response = requests.post(ML_CLIENT_URL, files={"image": image})
        if response.status_code == 200:
            emotion = response.json().get("emotion", "Unknown")
            return render_template("result.html", emotion=emotion)
        else:
            error = response.json().get("error", "An error occurred")
            return render_template("error.html", error=error)

    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        if users_collection.find_one({"username": username}):
            return "Username already exists", 400
        
        users_collection.insert_one({"username": username, "password": hashed_password})
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the last captured emotion data for the user
    last_emotion = emotion_data_collection.find_one({"user_id": session['user_id']}, sort=[("timestamp", -1)])
    return render_template('dashboard.html', last_emotion=last_emotion)

@app.route('/capture_emotion')
def capture_emotion():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    if not success:
        camera.release()
        return jsonify({"error": "Could not capture image"}), 500

    emotion_text = detect_emotion(frame)
    camera.release()

    # Save emotion and user information to MongoDB
    emotion_data_collection.insert_one({
        "user_id": session['user_id'],
        "emotion": emotion_text,
        "timestamp": datetime.utcnow()
    })

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)