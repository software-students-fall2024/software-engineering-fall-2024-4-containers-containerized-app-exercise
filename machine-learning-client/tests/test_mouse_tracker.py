"""
Unit tests for the MouseMetrics class in mouse_tracker.py.
"""

import pytest
from mouse_tracker import MouseMetrics

@pytest.fixture
def mouse_metrics_instance():
    """
    Fixture for creating a MouseMetrics instance.
    """
    return MouseMetrics()

def test_initial_metrics(metrics_instance):
    """
    Test that the MouseMetrics instance initializes with default values.
    """
    assert metrics_instance.mouse_distance == 0
    assert metrics_instance.click_count == 0
    assert metrics_instance.focused_time == 0
    assert metrics_instance.unfocused_time == 0
    assert metrics_instance.last_x is None
    assert metrics_instance.last_y is None

def test_process_mouse_move(metrics_instance):
    """
    Test the process_mouse_move method for calculating distance.
    """
    metrics_instance.process_mouse_move(0, 0)
    metrics_instance.process_mouse_move(3, 4)  # Distance = 5
    assert metrics_instance.mouse_distance == 5

def test_process_mouse_click(metrics_instance):
    """
    Test the process_mouse_click method to count clicks.
    """
    metrics_instance.process_mouse_click()
    metrics_instance.process_mouse_click()
    assert metrics_instance.click_count == 2

def test_generate_report(metrics_instance):
    """
    Test the generate_report method for accurate metrics.
    """
    metrics_instance.process_mouse_move(0, 0)
    metrics_instance.process_mouse_move(3, 4)
    metrics_instance.process_mouse_click()
    metrics_instance.focused_time = 10
    metrics_instance.unfocused_time = 5

    report = metrics_instance.generate_report()
    assert report["total_mouse_distance"] == 5
    assert report["click_count"] == 1
    assert report["focused_time"] == 10
    assert report["unfocused_time"] == 5
    assert report["focus_percentage"] == 66.67
    assert report["status"] == "Focused"

def test_sanitize_invalid_floats(metrics_instance):
    """
    Test that invalid floats are sanitized in the report.
    """
    metrics_instance.mouse_distance = float("nan")
    metrics_instance.focused_time = float("inf")
    report = metrics_instance.generate_report()

    assert report["total_mouse_distance"] == 0
    assert report["focused_time"] == 0
