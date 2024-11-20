"""
Mouse Activity Tracker

This module tracks mouse movement, clicks, and scrolls to monitor user focus.
It generates a final report summarizing user activity.
"""
import time
from pynput import mouse
import math
from dataclasses import dataclass
from pymongo import MongoClient

# MongoDB connection URI
MONGODB_URI = (
    "mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/"
    "?retryWrites=true&w=majority&appName=itsOver"
)
try:
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client["itsOver"]
    mouse_collection = db["mouse_activity"]

    # Test connection by inserting a test document
    test_document = {"test": "connection", "timestamp": time.time()}
    result = mouse_collection.insert_one(test_document)

    print(f"Connected to MongoDB successfully! Test document ID: {result.inserted_id}")

    # Fetch the inserted document
    fetched_document = mouse_collection.find_one({"_id": result.inserted_id})
    print(f"Fetched document: {fetched_document}")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")


FOCUS_THRESHOLD = 5  # Time (in seconds) before marking the user as unfocused


@dataclass
class MouseMetrics:
    """Group metrics related to mouse activity."""

    mouse_distance: float = 0
    click_count: int = 0
    scroll_distance: float = 0
    last_x: float = None
    last_y: float = None


class MouseTracker:
    """Tracks mouse activity and calculates focus metrics."""

    def __init__(self):
        self.last_event_time = time.time()
        self.metrics = MouseMetrics()
        self.focused_time = 0
        self.unfocused_time = 0
        self.is_focused = True

    def update_focus_state(self):
        """Updates the focus state based on recent mouse activity."""
        current_time = time.time()
        time_since_last_event = current_time - self.last_event_time

        if time_since_last_event > FOCUS_THRESHOLD:
            if self.is_focused:
                self.is_focused = False
                print(
                    f"Warning: Student is not focused! "
                    f"No activity for {time_since_last_event:.2f} seconds."
                )
            self.unfocused_time += time_since_last_event - FOCUS_THRESHOLD
        else:
            if not self.is_focused:
                self.is_focused = True
                print("Student regained focus.")
            self.focused_time += time_since_last_event

    def on_move(self, x, y):
        """Handles mouse movement events."""
        current_time = time.time()
        time_interval = current_time - self.last_event_time
        self.last_event_time = current_time

        if self.metrics.last_x is not None and self.metrics.last_y is not None:
            distance = math.sqrt(
                (x - self.metrics.last_x) ** 2 + (y - self.metrics.last_y) ** 2
            )
            self.metrics.mouse_distance += distance
            print(
                f"Mouse moved to ({x}, {y}), Time interval: {time_interval:.2f} seconds"
            )
            print(
                f"Distance moved: {distance:.2f} pixels, "
                f"Total distance: {self.metrics.mouse_distance:.2f} pixels"
            )
        self.metrics.last_x, self.metrics.last_y = x, y

        self.update_focus_state()

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        current_time = time.time()
        time_interval = current_time - self.last_event_time
        self.last_event_time = current_time

        action = "pressed" if pressed else "released"
        print(
            f"Mouse {action} at ({x}, {y}) with {button}, "
            f"Time interval: {time_interval:.2f} seconds"
        )

        if pressed:
            self.metrics.click_count += 1
            print(f"Click count: {self.metrics.click_count}")

        self.update_focus_state()

    def on_scroll(self, x, y, dx, dy):
        """Handles mouse scroll events."""
        current_time = time.time()
        time_interval = current_time - self.last_event_time
        self.last_event_time = current_time

        self.metrics.scroll_distance += abs(dy)
        print(
            f"Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy}), "
            f"Time interval: {time_interval:.2f} seconds"
        )
        print(
            f"Scroll distance: {abs(dy)}, Total scroll distance: {self.metrics.scroll_distance}"
        )

        self.update_focus_state()

    def generate_final_report(self):
        """Generates and prints a final activity report."""
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (
            (self.focused_time / total_time) * 100 if total_time > 0 else 0
        )
        unfocus_percentage = 100 - focus_percentage

        print("\n--- Final Report ---")
        print(f"Total mouse distance moved: {self.metrics.mouse_distance:.2f} pixels")
        print(f"Total clicks: {self.metrics.click_count}")
        print(f"Total scrolls: {self.metrics.scroll_distance}")
        print(
            f"Focused time: {self.focused_time:.2f} seconds ({focus_percentage:.2f}%)"
        )
        print(
            f"Unfocused time: {self.unfocused_time:.2f} seconds ({unfocus_percentage:.2f}%)"
        )
        print(
            f"Student was {'Focused' if focus_percentage > unfocus_percentage else 'Unfocused'} "
            f"during the class."
        )
        print("------------------------")

    def generate_final_report(self):
        """Generate a final report in dictionary format and print it."""
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (
            (self.focused_time / total_time) * 100 if total_time > 0 else 0
        )
        unfocus_percentage = 100 - focus_percentage

        # Create a report dictionary
        report = {
            "total_mouse_distance": round(self.metrics.mouse_distance, 2),
            "total_clicks": self.metrics.click_count,
            "total_scrolls": self.metrics.scroll_distance,
            "focused_time": round(self.focused_time, 2),
            "unfocused_time": round(self.unfocused_time, 2),
            "focus_percentage": round(focus_percentage, 2),
            "unfocus_percentage": round(unfocus_percentage, 2),
            "overall_status": "Focused" if focus_percentage > unfocus_percentage else "Unfocused",
        }
        return report
    
    def save_to_database(self, report):
        """Saves the final report to MongoDB."""
        try:
            result = mouse_collection.insert_one(report)  # Insert the report into the collection
            print(f"Final report saved to MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            print(f"Failed to save report to MongoDB: {e}")

if __name__ == "__main__":
    tracker = MouseTracker()

    with mouse.Listener(
        on_move=tracker.on_move, on_click=tracker.on_click, on_scroll=tracker.on_scroll
    ) as listener:
        print("Listening for mouse events... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
                tracker.update_focus_state()
        except KeyboardInterrupt:
            print("\nStopped monitoring.")
            # Generate the final report
            report = tracker.generate_final_report()
            # Save the final report to MongoDB
            tracker.save_to_database(report)

