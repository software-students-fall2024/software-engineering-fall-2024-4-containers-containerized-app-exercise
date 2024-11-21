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


# pylint: disable=redefined-outer-name
def test_initial_metrics(mouse_metrics_instance):
    """
    Test that the MouseMetrics instance initializes with default values.
    """
    assert mouse_metrics_instance.mouse_distance == 0
    assert mouse_metrics_instance.click_count == 0
    assert mouse_metrics_instance.focused_time == 0
    assert mouse_metrics_instance.unfocused_time == 0
    assert mouse_metrics_instance.last_x is None
    assert mouse_metrics_instance.last_y is None


def test_process_mouse_move(mouse_metrics_instance):
    """
    Test the process_mouse_move method for calculating distance.
    """
    mouse_metrics_instance.process_mouse_move(0, 0)
    mouse_metrics_instance.process_mouse_move(3, 4)  # Distance = 5
    assert mouse_metrics_instance.mouse_distance == 5


def test_process_mouse_click(mouse_metrics_instance):
    """
    Test the process_mouse_click method to count clicks.
    """
    mouse_metrics_instance.process_mouse_click()
    mouse_metrics_instance.process_mouse_click()
    assert mouse_metrics_instance.click_count == 2


def test_generate_report(mouse_metrics_instance):
    """
    Test the generate_report method for accurate metrics.
    """
    mouse_metrics_instance.process_mouse_move(0, 0)
    mouse_metrics_instance.process_mouse_move(3, 4)
    mouse_metrics_instance.process_mouse_click()
    mouse_metrics_instance.focused_time = 10
    mouse_metrics_instance.unfocused_time = 5

    report = mouse_metrics_instance.generate_report()
    assert report["total_mouse_distance"] == 5
    assert report["click_count"] == 1
    assert report["focused_time"] == 10
    assert report["unfocused_time"] == 5
    assert report["focus_percentage"] == 66.67
    assert report["status"] == "Focused"


def test_sanitize_invalid_floats(mouse_metrics_instance):
    """
    Test that invalid floats are sanitized in the report.
    """
    mouse_metrics_instance.mouse_distance = float("nan")
    mouse_metrics_instance.focused_time = float("inf")
    report = mouse_metrics_instance.generate_report()

    assert report["total_mouse_distance"] == 0
    assert report["focused_time"] == 0


def test_reset_metrics(mouse_metrics_instance):
    """
    Test the reset_metrics method to ensure all metrics are reset correctly.
    """
    mouse_metrics_instance.process_mouse_move(0, 0)
    mouse_metrics_instance.process_mouse_move(3, 4)
    mouse_metrics_instance.process_mouse_click()
    mouse_metrics_instance.reset_metrics()

    assert mouse_metrics_instance.mouse_distance == 0
    assert mouse_metrics_instance.click_count == 0
    assert mouse_metrics_instance.focused_time == 0
    assert mouse_metrics_instance.unfocused_time == 0
    assert mouse_metrics_instance.last_x is None
    assert mouse_metrics_instance.last_y is None


def test_process_mouse_move_invalid_input(mouse_metrics_instance):
    """
    Test process_mouse_move with invalid inputs.
    """
    mouse_metrics_instance.process_mouse_move(0, 0)
    with pytest.raises(TypeError):
        mouse_metrics_instance.process_mouse_move(None, 5)
    with pytest.raises(TypeError):
        mouse_metrics_instance.process_mouse_move("a", "b")


def test_generate_report_no_activity(mouse_metrics_instance):
    """
    Test generate_report when no activity has been recorded.
    """
    report = mouse_metrics_instance.generate_report()
    assert report["total_mouse_distance"] == 0
    assert report["click_count"] == 0
    assert report["focused_time"] == 0
    assert report["unfocused_time"] == 0
    assert report["focus_percentage"] == 0
    assert report["status"] == "Unfocused"
