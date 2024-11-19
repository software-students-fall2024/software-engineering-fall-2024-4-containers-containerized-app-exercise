"""
Mouse Activity Tracker
Tracks mouse movement, clicks, and scrolls to monitor user focus. Generates a final report.
"""

import time
import math
from pynput import mouse

FOCUS_THRESHOLD = 5  # Time (in seconds) before marking the user as unfocused


class MouseTracker:
    """Tracks mouse activity and calculates focus metrics."""

    def __init__(self):
        self.last_event_time = time.time()
        self.metrics = {
            "mouse_distance": 0,
            "click_count": 0,
            "scroll_distance": 0,
            "focused_time": 0,
            "unfocused_time": 0,
        }
        self.last_position = {"x": None, "y": None}
        self.is_focused = True

    def update_focus_state(self):
        """Updates the focus state based on recent mouse activity."""
        current_time = time.time()
        time_since_last_event = current_time - self.last_event_time

        if time_since_last_event > FOCUS_THRESHOLD:
            if self.is_focused:
                self.is_focused = False
                print(
                    f"Warning: No activity for {time_since_last_event:.2f} seconds."
                )
            self.metrics["unfocused_time"] += time_since_last_event - FOCUS_THRESHOLD
        else:
            if not self.is_focused:
                self.is_focused = True
                print("Focus regained.")
            self.metrics["focused_time"] += time_since_last_event

    def on_move(self, x, y):
        """Handles mouse movement events."""
        current_time = time.time()
        self.last_event_time = current_time

        if self.last_position["x"] is not None and self.last_position["y"] is not None:
            distance = math.sqrt(
                (x - self.last_position["x"]) ** 2
                + (y - self.last_position["y"]) ** 2
            )
            self.metrics["mouse_distance"] += distance
            print(
                f"Mouse moved to ({x}, {y}), Distance: {distance:.2f} pixels"
            )
        self.last_position["x"], self.last_position["y"] = x, y
        self.update_focus_state()

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        self.last_event_time = time.time()

        if pressed:
            self.metrics["click_count"] += 1
            print(
                f"Mouse clicked at ({x}, {y}) with {button}. "
                f"Total clicks: {self.metrics['click_count']}"
            )
        self.update_focus_state()

    def on_scroll(self, x, y, _, dy):
        """Handles mouse scroll events."""
        self.last_event_time = time.time()
        self.metrics["scroll_distance"] += abs(dy)
        print(
            f"Mouse scrolled at ({x}, {y}), Scroll delta: {dy}, "
            f"Total scrolls: {self.metrics['scroll_distance']}"
        )
        self.update_focus_state()

    def generate_final_report(self):
        """Generates and prints a final activity report."""
        total_time = self.metrics["focused_time"] + self.metrics["unfocused_time"]
        focus_percentage = (
            (self.metrics["focused_time"] / total_time) * 100 if total_time > 0 else 0
        )
        unfocus_percentage = 100 - focus_percentage

        print("\n--- Final Report ---")
        print(f"Total mouse distance moved: {self.metrics['mouse_distance']:.2f} pixels")
        print(f"Total clicks: {self.metrics['click_count']}")
        print(f"Total scrolls: {self.metrics['scroll_distance']}")
        print(f"Focused time: {self.metrics['focused_time']:.2f} seconds "
              f"({focus_percentage:.2f}%)")
        print(f"Unfocused time: {self.metrics['unfocused_time']:.2f} seconds "
              f"({unfocus_percentage:.2f}%)")
        print(f"Student was {'Focused' if focus_percentage > unfocus_percentage else 'Unfocused'} "
              f"during the class.")
        print("------------------------")


if __name__ == "__main__":
    tracker = MouseTracker()

    with mouse.Listener(
        on_move=tracker.on_move,
        on_click=tracker.on_click,
        on_scroll=tracker.on_scroll
    ) as listener:
        print("Listening for mouse events... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
                tracker.update_focus_state()
        except KeyboardInterrupt:
            tracker.generate_final_report()
