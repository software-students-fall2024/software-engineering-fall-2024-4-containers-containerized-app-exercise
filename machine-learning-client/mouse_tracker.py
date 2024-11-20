"""
Mouse Activity Tracker

This module tracks mouse movement, clicks, and scrolls to monitor user focus.
It generates a final report summarizing user activity.
"""

import time
import math
from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, WriteError
from pynput import mouse

# MongoDB connection URI
MONGODB_URI = (
    "mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/"
    "?retryWrites=true&w=majority&appName=itsOver"
)

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client["itsOver"]
    mouse_collection = db["mouse_activity"]

    # Test connection by inserting a test document
    test_document = {"test": "connection", "timestamp": time.time()}
    test_result = mouse_collection.insert_one(test_document)
    print(
        f"Connected to MongoDB successfully! Test document ID: {test_result.inserted_id}"
    )
except (ConnectionFailure, OperationFailure) as error:
    print(f"Failed to connect to MongoDB: {error}")


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
        self.last_event_time = current_time

        if self.metrics.last_x is not None and self.metrics.last_y is not None:
            distance = math.sqrt(
                (x - self.metrics.last_x) ** 2 + (y - self.metrics.last_y) ** 2
            )
            self.metrics.mouse_distance += distance
            print(f"Mouse moved to ({x}, {y}), Distance: {distance:.2f} pixels")

        self.metrics.last_x, self.metrics.last_y = x, y
        self.update_focus_state()

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        self.last_event_time = time.time()
        action = "pressed" if pressed else "released"
        print(f"Mouse {action} at ({x}, {y}) with {button}")

        if pressed:
            self.metrics.click_count += 1
            print(f"Click count: {self.metrics.click_count}")

        self.update_focus_state()

    def on_scroll(self, x, y, dx, dy):
        """Handles mouse scroll events."""
        self.last_event_time = time.time()
        self.metrics.scroll_distance += abs(dy)
        print(f"Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy})")

        self.update_focus_state()

    def generate_final_report(self):
        """Generate a final report in dictionary format."""
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (
            (self.focused_time / total_time) * 100 if total_time > 0 else 0
        )
        unfocus_percentage = 100 - focus_percentage

        report = {
            "total_mouse_distance": round(self.metrics.mouse_distance, 2),
            "total_clicks": self.metrics.click_count,
            "total_scrolls": self.metrics.scroll_distance,
            "focused_time": round(self.focused_time, 2),
            "unfocused_time": round(self.unfocused_time, 2),
            "focus_percentage": round(focus_percentage, 2),
            "unfocus_percentage": round(unfocus_percentage, 2),
            "overall_status": (
                "Focused" if focus_percentage > unfocus_percentage else "Unfocused"
            ),
        }
        return report

    def save_to_database(self, report):
        """Saves the final report to MongoDB."""
        try:
            result = mouse_collection.insert_one(report)
            print(f"Final report saved to MongoDB with ID: {result.inserted_id}")
        except WriteError as error:
            print(f"Failed to save report to MongoDB: {error}")


class MouseTrackerWithInterface(MouseTracker):
    """Mouse Tracker with start and stop interfaces."""

    def __init__(self):
        super().__init__()
        self.listener = None

    def start_tracking(self):
        """Start mouse tracking."""
        if not self.listener:
            self.listener = mouse.Listener(
                on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
            )
            self.listener.start()
            print("Mouse tracking started.")

    def stop_tracking(self):
        """Stop mouse tracking."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Mouse tracking stopped.")
            # Generate and save the final report after stopping
            final_report = self.generate_final_report()
            self.save_to_database(final_report)


if __name__ == "__main__":
    try:
        tracker = MouseTrackerWithInterface()

        print("Starting mouse tracking...")
        tracker.start_tracking()

        try:
            # Run indefinitely until manually stopped
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Handle manual interruption (Ctrl+C)
            print("\nManual interruption detected. Stopping mouse tracking...")
        finally:
            # Ensure tracker is stopped properly
            tracker.stop_tracking()
            print("\nMouse tracking stopped. Generating final report...")

    except (ConnectionFailure, OperationFailure, WriteError) as db_error:
        # Handle database-related exceptions
        print(f"A database error occurred: {db_error}")
    except ValueError as value_error:
        # Handle specific logical errors, if any
        print(f"A value error occurred: {value_error}")
    except KeyboardInterrupt:
        # Ensure manual interruptions are explicitly logged
        print("\nProgram was manually interrupted.")
    except RuntimeError as runtime_error:
        # Handle runtime-related errors
        print(f"A runtime error occurred: {runtime_error}")
    except Exception as e:
        # Fallback for unexpected errors, with detailed logging
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the tracker is stopped if it was initialized
        try:
            if "tracker" in locals() and isinstance(tracker, MouseTrackerWithInterface):
                tracker.stop_tracking()
        except Exception as cleanup_error:
            # Log any errors that occur during cleanup
            print(f"An error occurred while stopping the tracker: {cleanup_error}")
