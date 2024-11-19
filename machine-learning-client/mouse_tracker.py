from pynput import mouse
import time
import math


last_event_time = time.time()  
mouse_distance = 0  
click_count = 0  
scroll_distance = 0  


last_x, last_y = None, None


focused_time = 0  
unfocused_time = 0  
is_focused = True  


FOCUS_THRESHOLD = 5  

def update_focus_state():
    global is_focused, unfocused_time, focused_time

    current_time = time.time()
    time_since_last_event = current_time - last_event_time

    if time_since_last_event > FOCUS_THRESHOLD:
        if is_focused:
            is_focused = False
            print(f"Warning: Student is not focused! No activity for {time_since_last_event:.2f} seconds.")
        unfocused_time += time_since_last_event - FOCUS_THRESHOLD
    else:
        if not is_focused:
            is_focused = True
            print("Student regained focus.")
        focused_time += time_since_last_event


def on_move(x, y):
    global last_event_time, last_x, last_y, mouse_distance

    current_time = time.time()
    time_interval = current_time - last_event_time
    last_event_time = current_time


    if last_x is not None and last_y is not None:
        distance = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
        mouse_distance += distance
        print(f"Mouse moved to ({x}, {y}), Time interval: {time_interval:.2f} seconds")
        print(f"Distance moved: {distance:.2f} pixels, Total distance: {mouse_distance:.2f} pixels")
    last_x, last_y = x, y

    update_focus_state()

def on_click(x, y, button, pressed):
    global last_event_time, click_count

    current_time = time.time()
    time_interval = current_time - last_event_time
    last_event_time = current_time

    action = "pressed" if pressed else "released"
    print(f"Mouse {action} at ({x}, {y}) with {button}, Time interval: {time_interval:.2f} seconds")
    
    if pressed:
        click_count += 1
        print(f"Click count: {click_count}")

    update_focus_state()

def on_scroll(x, y, dx, dy):
    global last_event_time, scroll_distance

    current_time = time.time()
    time_interval = current_time - last_event_time
    last_event_time = current_time

    scroll_distance += abs(dy)
    print(f"Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy}), Time interval: {time_interval:.2f} seconds")
    print(f"Scroll distance: {abs(dy)}, Total scroll distance: {scroll_distance}")

    update_focus_state()

def generate_final_report():
    total_time = focused_time + unfocused_time
    focus_percentage = (focused_time / total_time) * 100 if total_time > 0 else 0
    unfocus_percentage = 100 - focus_percentage

    print("\n--- Final Report ---")
    print(f"Total mouse distance moved: {mouse_distance:.2f} pixels")
    print(f"Total clicks: {click_count}")
    print(f"Total scrolls: {scroll_distance}")
    print(f"Focused time: {focused_time:.2f} seconds ({focus_percentage:.2f}%)")
    print(f"Unfocused time: {unfocused_time:.2f} seconds ({unfocus_percentage:.2f}%)")
    print(f"Student was {'Focused' if focus_percentage > unfocus_percentage else 'Unfocused'} during the class.")
    print("------------------------")


with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    print("Listening for mouse events... (Press Ctrl+C to stop)")
    try:
        while True:

            time.sleep(1)
            update_focus_state()
    except KeyboardInterrupt:

        generate_final_report()

