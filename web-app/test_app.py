"""
This module contains tests for the Web App. Run with 'python -m pytest test_app.py'
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import app


@pytest.fixture(name="test_client")
def fixture_test_client():
    """Mock client fixture"""
    with app.test_client() as client:
        yield client


def test_index_page(
    test_client,
):  # Use 'client' as the argument name to match the fixture
    """Test the index page route."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Real-Time Object Detection" in response.data


def test_dashboard_page(test_client):  # Use 'client' as the argument name
    """Test the dashboard page."""
    response = test_client.get("/dashboard")  # Ensure this route exists
    assert response.status_code == 200
    assert b"Object Detection Trends" in response.data


def test_api_detect(test_client):  # Use 'client' as the argument name
    """Test the object detection API endpoint."""
    response = test_client.post("/api/detect")  # Ensure this route exists
    assert response.status_code == 200
    assert (
        "objects" in response.json
    )  # Check if 'objects' is a key in the JSON response
    assert isinstance(
        response.json["objects"], list
    )  # Optionally, check that 'objects' is a list
    assert (
        len(response.json["objects"]) == 0
    )  # You can also check that the list is empty
