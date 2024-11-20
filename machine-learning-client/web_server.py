"a Flask-based web server that serves a simple webpage"

from flask import Flask, render_template, jsonify
import subprocess
import os
import signal

app = Flask(__name__)
tracker_process = None  # Global variable to track the camera_tracker process

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start-tracking", methods=["POST"])
def start_tracking():
    global tracker_process
    if tracker_process is None:
        # Start the camera_tracker.py process
        tracker_process = subprocess.Popen(["python", "camera_tracker.py"])
        return jsonify({"status": "Tracking started"})
    else:
        return jsonify({"status": "Tracking already running"})

@app.route("/stop-tracking", methods=["POST"])
def stop_tracking():
    global tracker_process
    if tracker_process is not None:
        # Terminate the camera_tracker.py process
        tracker_process.terminate()
        tracker_process.wait()
        tracker_process = None
        return jsonify({"status": "Tracking stopped"})
    else:
        return jsonify({"status": "No tracking process running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
