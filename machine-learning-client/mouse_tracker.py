from flask import Blueprint, request, jsonify
import time
import math


class MouseMetrics:
    def __init__(self):
        self.mouse_distance = 0
        self.click_count = 0
        self.focused_time = 0
        self.unfocused_time = 0
        self.last_x = None
        self.last_y = None
        self.last_event_time = time.time()
        self.FOCUS_THRESHOLD = 5

    def process_mouse_move(self, x, y):
        current_time = time.time()
        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            self.mouse_distance += distance
        self.last_x, self.last_y = x, y
        if current_time - self.last_event_time > self.FOCUS_THRESHOLD:
            self.unfocused_time += (
                current_time - self.last_event_time - self.FOCUS_THRESHOLD
            )
        else:
            self.focused_time += current_time - self.last_event_time
        self.last_event_time = current_time

    def process_mouse_click(self):
        self.click_count += 1


def generate_report(self):
    total_time = self.focused_time + self.unfocused_time
    focus_percentage = (self.focused_time / total_time) * 100 if total_time > 0 else 0

    # Build the report
    report = {
        "total_mouse_distance": round(self.mouse_distance, 2),
        "click_count": self.click_count,
        "focused_time": round(self.focused_time, 2),
        "unfocused_time": round(self.unfocused_time, 2),
        "focus_percentage": round(focus_percentage, 2),
        "status": "Focused" if focus_percentage > 50 else "Unfocused",
    }

    # Sanitize the report
    for key, value in report.items():
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            report[key] = 0  # Replace invalid floats with 0

    return report


mouse_metrics = MouseMetrics()


def init_mouse_routes(app, db):
    mouse_bp = Blueprint("mouse", __name__)

    @mouse_bp.route("/track-mouse", methods=["POST"])
    def track_mouse():
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
        return jsonify(mouse_metrics.generate_report()), 200

    app.register_blueprint(mouse_bp)
