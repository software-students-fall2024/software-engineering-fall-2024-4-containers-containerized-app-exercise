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

# Set up MongoDB connection (update with your MongoDB details)
client = MongoClient("mongodb://localhost:27017/")
db = client['traffic_db']
traffic_data_collection = db['traffic_data']

# Generate frames from camera and use ML client to detect emotion
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            emotion_text = detect_emotion(frame)

            # Save the detected emotion and timestamp to MongoDB
            traffic_data_collection.insert_one({
                "emotion": emotion_text,
                "timestamp": datetime.now()
            })

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame as multipart/jpeg and emotion as JSON
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n',
                   emotion_text)

@app.route('/video_feed')
def video_feed():
    # Stream the video frames
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    # Render the main HTML page
    return render_template('index.html')

@app.route('/emotion')
def emotion():
    # Fetch the latest emotion detected from the camera feed
    _, emotion_text = next(gen_frames())
    return jsonify({'emotion': emotion_text})

if __name__ == '__main__':
    app.run(debug=True)
