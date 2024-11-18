"""
This module contains test cases for the Flask application using pytest.
"""

# pylint: disable=redefined-outer-name
import pytest
from app import app  # Import the main application module


# Fixture to provide a test client for the Flask application
@pytest.fixture
def client():
    """
    Create a test client for the Flask application.
    """
    with app.test_client() as client:
        yield client


def test_home_route(client):
    """
    Test the home route to ensure it returns a status code of 200
    and includes a title in the response.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"<title>" in response.data


def test_tutorial_route(client):
    """
    Test the tutorial route to ensure it returns a status code of 200
    and includes a title in the response.
    """
    response = client.get("/tutorial")
    assert response.status_code == 200
    assert b"<title>" in response.data


def test_game_route(client):
    """
    Test the game route to ensure it returns a status code of 200.
    """
    response = client.get("/game")
    assert response.status_code == 200


def test_stats_route(client):
    """
    Test the stats route to ensure it returns a status code of 200.
    """
    response = client.get("/stats")
    assert response.status_code == 200


def test_data_route(client):
    """
    Test the JSON data API to ensure it returns a success status and includes a data key.
    """
    response = client.get("/data")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert "data" in json_data


def test_test_db_route(client):
    """
    Test the MongoDB connection route to verify success or error status.
    """
    response = client.get("/test-db")
    json_data = response.get_json()
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        assert json_data["status"] == "success"
    else:
        assert json_data["status"] == "error"


def test_add_data_route(client):
    """
    Test the add_data route to ensure it returns an error for unimplemented functionality.
    """
    response = client.post("/add_data")
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Error adding data" in json_data["message"]
