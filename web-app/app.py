from flask import Flask, render_template, Response, jsonify
from pymongo import MongoClient
from datetime import datetime
import cv2
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from machine_learning_client.ml_client import detect_emotion

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["emotion_db"]
emotion_data_collection = db["emotion_data"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture_emotion')
def capture_enotion():
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    if not success:
        camera.release()
        return jsonify({"error": "could not capture image"}), 500
    emotion_text = detect_emotion(frame)
    camera.release()
    return jsonify({"emotion": emotion_text})

if __name__ == '__main__':
    app.run(debug=True)


