"""
Web server for managing camera tracking.
"""

import subprocess  # Standard import first
from flask import Flask, render_template, jsonify  # Third-party imports

app = Flask(__name__)
TRACKER_PROCESS = None  # Global variable to track the camera_tracker process


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")


@app.route("/start-tracking", methods=["POST"])
def start_tracking():
    """Start the camera tracking process."""
    global TRACKER_PROCESS  # pylint: disable=global-statement
    if TRACKER_PROCESS is None:
        # Use 'with' for better resource management
        with subprocess.Popen(["python", "camera_tracker.py"]) as process:
            TRACKER_PROCESS = process
            return jsonify({"status": "Tracking started"})
    return jsonify({"status": "Tracking already running"})


@app.route("/stop-tracking", methods=["POST"])
def stop_tracking():
    """Stop the camera tracking process."""
    global TRACKER_PROCESS  # pylint: disable=global-statement
    if TRACKER_PROCESS is not None:
        TRACKER_PROCESS.terminate()
        TRACKER_PROCESS.wait()
        TRACKER_PROCESS = None
        return jsonify({"status": "Tracking stopped"})
    return jsonify({"status": "No tracking process running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
