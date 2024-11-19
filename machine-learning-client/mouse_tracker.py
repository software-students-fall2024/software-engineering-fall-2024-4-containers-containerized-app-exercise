"""
Mouse Activity Tracker

This module tracks mouse movement, clicks, and scrolls to monitor user focus.
It generates a final report summarizing user activity.
"""

from dataclasses import dataclass
import time
import math
from pynput import mouse

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
            tracker.generate_final_report()
