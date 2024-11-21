"""
Mouse tracking metrics and routes for Flask application.
"""

import math
import time
from flask import Blueprint, request, jsonify


class MouseMetrics:
    """
    A class to handle and process mouse tracking metrics.
    """

    FOCUS_THRESHOLD = 5  # Time in seconds to determine focus

    def __init__(self):
        """
        Initialize mouse metrics with default values.
        """
        self.mouse_distance = 0
        self.click_count = 0
        self.focused_time = 0
        self.unfocused_time = 0
        self.last_x = None
        self.last_y = None
        self.last_event_time = time.time()

    def reset_metrics(self):
        """
        Reset all mouse metrics to their initial values.
        """
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
        Args:
            x (float): Current X coordinate of the mouse.
            y (float): Current Y coordinate of the mouse.
        """
        current_time = time.time()
        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            self.mouse_distance += distance
        self.last_x, self.last_y = x, y
        time_since_last_event = current_time - self.last_event_time

        if time_since_last_event > self.FOCUS_THRESHOLD:
            self.unfocused_time += time_since_last_event - self.FOCUS_THRESHOLD
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

        Returns:
            dict: A dictionary containing the mouse metrics report.
        """
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (self.focused_time / total_time) * 100 if total_time > 0 else 0

        report = {
            "total_mouse_distance": round(self.mouse_distance, 2),
            "click_count": self.click_count,
            "focused_time": round(self.focused_time, 2),
            "unfocused_time": round(self.unfocused_time, 2),
            "focus_percentage": round(focus_percentage, 2),
            "status": "Focused" if focus_percentage > 50 else "Unfocused",
        }

        # Sanitize invalid floats
        for key, value in report.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                report[key] = 0

        return report


mouse_metrics = MouseMetrics()


def init_mouse_routes(app, db):
    """
    Initialize mouse tracking routes for the Flask application.

    Args:
        app (Flask): The Flask application instance.
        db (pymongo.Database): The MongoDB database instance.
    """
    mouse_bp = Blueprint("mouse", __name__)

    @mouse_bp.route("/track-mouse", methods=["POST"])
    def track_mouse():
        """
        Route to handle mouse tracking events (mousemove or click).
        """
        data = request.json
        event = data.get("event")
        x, y = data.get("x"), data.get("y")
        if event == "mousemove":
            mouse_metrics.process_mouse_move(x, y)
        elif event == "click":
            mouse_metrics.process_mouse_click()
        db.mouse_activity.insert_one({**data, "timestamp": time.time()})
        return jsonify({"status": "success"}), 200

    @mouse_bp.route("/mouse-report", methods=["GET"])
    def mouse_report():
        """
        Route to generate and return the mouse tracking report.
        """
        report = mouse_metrics.generate_report()
        return jsonify(report), 200

    app.register_blueprint(mouse_bp)
