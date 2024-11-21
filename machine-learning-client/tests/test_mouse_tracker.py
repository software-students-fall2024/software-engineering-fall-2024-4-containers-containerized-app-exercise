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

<<<<<<< HEAD

# pylint: disable=redefined-outer-name
def test_initial_metrics(mouse_metrics):
=======
def test_initial_metrics(metrics_instance):
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
    """
    Test that the MouseMetrics instance initializes with default values.
    """
    assert metrics_instance.mouse_distance == 0
    assert metrics_instance.click_count == 0
    assert metrics_instance.focused_time == 0
    assert metrics_instance.unfocused_time == 0
    assert metrics_instance.last_x is None
    assert metrics_instance.last_y is None

<<<<<<< HEAD

def test_process_mouse_move(mouse_metrics):
=======
def test_process_mouse_move(metrics_instance):
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
    """
    Test the process_mouse_move method for calculating distance.
    """
    metrics_instance.process_mouse_move(0, 0)
    metrics_instance.process_mouse_move(3, 4)  # Distance = 5
    assert metrics_instance.mouse_distance == 5

<<<<<<< HEAD

def test_process_mouse_click(mouse_metrics):
=======
def test_process_mouse_click(metrics_instance):
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
    """
    Test the process_mouse_click method to count clicks.
    """
    metrics_instance.process_mouse_click()
    metrics_instance.process_mouse_click()
    assert metrics_instance.click_count == 2

<<<<<<< HEAD

def test_generate_report(mouse_metrics):
=======
def test_generate_report(metrics_instance):
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
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

<<<<<<< HEAD

def test_sanitize_invalid_floats(mouse_metrics):
=======
def test_sanitize_invalid_floats(metrics_instance):
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
    """
    Test that invalid floats are sanitized in the report.
    """
    metrics_instance.mouse_distance = float("nan")
    metrics_instance.focused_time = float("inf")
    report = metrics_instance.generate_report()

    assert report["total_mouse_distance"] == 0
    assert report["focused_time"] == 0
<<<<<<< HEAD


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
=======
>>>>>>> b740fe431351452f456b6020fd6a5ae9f92234cb
