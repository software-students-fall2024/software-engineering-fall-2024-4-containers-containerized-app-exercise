"""
Unit tests for the MouseMetrics class in mouse_tracker.py.
"""

import pytest
from mouse_tracker import MouseMetrics


@pytest.fixture
def mouse_metrics():
    """
    Fixture to create a new instance of MouseMetrics for each test.
    """
    return MouseMetrics()


# pylint: disable=redefined-outer-name
def test_initial_metrics(mouse_metrics):
    """
    Test that the MouseMetrics instance initializes correctly.
    """
    assert mouse_metrics.mouse_distance == 0
    assert mouse_metrics.click_count == 0
    assert mouse_metrics.focused_time == 0
    assert mouse_metrics.unfocused_time == 0
    assert mouse_metrics.last_x is None
    assert mouse_metrics.last_y is None


def test_process_mouse_move(mouse_metrics):
    """
    Test the process_mouse_move method.
    """
    mouse_metrics.process_mouse_move(0, 0)
    mouse_metrics.process_mouse_move(3, 4)  # Distance = 5 (3-4-5 triangle)
    assert mouse_metrics.mouse_distance == 5


def test_process_mouse_click(mouse_metrics):
    """
    Test the process_mouse_click method.
    """
    mouse_metrics.process_mouse_click()
    mouse_metrics.process_mouse_click()
    assert mouse_metrics.click_count == 2


def test_generate_report(mouse_metrics):
    """
    Test the generate_report method.
    """
    mouse_metrics.process_mouse_move(0, 0)
    mouse_metrics.process_mouse_move(3, 4)
    mouse_metrics.process_mouse_click()
    mouse_metrics.focused_time = 10
    mouse_metrics.unfocused_time = 5

    report = mouse_metrics.generate_report()
    assert report["total_mouse_distance"] == 5
    assert report["click_count"] == 1
    assert report["focused_time"] == 10
    assert report["unfocused_time"] == 5
    assert report["focus_percentage"] == 66.67  # 2/3 focus time
    assert report["status"] == "Focused"


def test_sanitize_invalid_floats(mouse_metrics):
    """
    Test that invalid floats in the report are sanitized.
    """
    mouse_metrics.mouse_distance = float("nan")
    mouse_metrics.focused_time = float("inf")
    report = mouse_metrics.generate_report()

    assert report["total_mouse_distance"] == 0
    assert report["focused_time"] == 0


def test_reset_metrics(mouse_metrics):
    """
    Test the reset_metrics method to ensure all metrics are reset correctly.
    """
    mouse_metrics.process_mouse_move(0, 0)
    mouse_metrics.process_mouse_move(3, 4)
    mouse_metrics.process_mouse_click()
    mouse_metrics.reset_metrics()

    assert mouse_metrics.mouse_distance == 0
    assert mouse_metrics.click_count == 0
    assert mouse_metrics.focused_time == 0
    assert mouse_metrics.unfocused_time == 0
    assert mouse_metrics.last_x is None
    assert mouse_metrics.last_y is None


def test_process_mouse_move_invalid_input(mouse_metrics):
    """
    Test process_mouse_move with invalid inputs.
    """
    mouse_metrics.process_mouse_move(0, 0)
    with pytest.raises(TypeError):
        mouse_metrics.process_mouse_move(None, 5)
    with pytest.raises(TypeError):
        mouse_metrics.process_mouse_move("a", "b")


def test_generate_report_no_activity(mouse_metrics):
    """
    Test generate_report when no activity has been recorded.
    """
    report = mouse_metrics.generate_report()
    assert report["total_mouse_distance"] == 0
    assert report["click_count"] == 0
    assert report["focused_time"] == 0
    assert report["unfocused_time"] == 0
    assert report["focus_percentage"] == 0
    assert report["status"] == "Unfocused"
