import time
import math
from pynput import mouse

FOCUS_THRESHOLD = 5  # Time (in seconds) before marking the user as unfocused


class MouseTracker:
    """Tracks mouse activity and calculates focus metrics."""

    def __init__(self):
        self.last_event_time = time.time()
        self.mouse_distance = 0
        self.click_count = 0
        self.scroll_distance = 0
        self.last_x = None
        self.last_y = None
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
                print(f"User unfocused! No activity for {time_since_last_event:.2f} seconds.")
            self.unfocused_time += time_since_last_event - FOCUS_THRESHOLD
        else:
            if not self.is_focused:
                self.is_focused = True
                print("User regained focus.")
            self.focused_time += time_since_last_event

    def on_move(self, x, y):
        """Handles mouse movement events."""
        current_time = time.time()
        self.last_event_time = current_time

        if self.last_x is not None and self.last_y is not None:
            distance = math.sqrt((x - self.last_x) ** 2 + (y - self.last_y) ** 2)
            self.mouse_distance += distance
            print(f"Mouse moved to ({x}, {y}), Distance: {distance:.2f} pixels, "
                  f"Total distance: {self.mouse_distance:.2f} pixels")
        self.last_x, self.last_y = x, y
        self.update_focus_state()

    def on_click(self, x, y, button, pressed):
        """Handles mouse click events."""
        current_time = time.time()
        self.last_event_time = current_time

        if pressed:
            self.click_count += 1
            print(f"Mouse clicked at ({x}, {y}) with {button}, Total clicks: {self.click_count}")

        self.update_focus_state()

    def on_scroll(self, x, y, dx, dy):
        """Handles mouse scroll events."""
        current_time = time.time()
        self.last_event_time = current_time

        self.scroll_distance += abs(dy)
        print(f"Mouse scrolled at ({x}, {y}), Scroll delta: {dy}, "
              f"Total scroll distance: {self.scroll_distance}")

        self.update_focus_state()

    def generate_final_report(self):
        """Generates and prints a final activity report."""
        total_time = self.focused_time + self.unfocused_time
        focus_percentage = (self.focused_time / total_time) * 100 if total_time > 0 else 0
        unfocus_percentage = 100 - focus_percentage

        print("\n--- Final Report ---")
        print(f"Total mouse distance moved: {self.mouse_distance:.2f} pixels")
        print(f"Total clicks: {self.click_count}")
        print(f"Total scrolls: {self.scroll_distance}")
        print(f"Focused time: {self.focused_time:.2f} seconds ({focus_percentage:.2f}%)")
        print(f"Unfocused time: {self.unfocused_time:.2f} seconds ({unfocus_percentage:.2f}%)")
        print(f"User was {'Focused' if focus_percentage > unfocus_percentage else 'Unfocused'} "
              f"during the session.")
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
