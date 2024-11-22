"""
This module contains test cases for the Flask application using pytest.
"""

import pytest
from app import app, simulate_computer_choice, determine_result  

# Rename the fixture to avoid conflict
@pytest.fixture
def test_client():
    """
    Create a test client for the Flask application.
    """
    with app.test_client() as client:
        yield client

 

def test_home_route(test_client): # noqa
    """
    Test the home route to ensure it returns a status code of 200.
    """
    response = test_client.get("/")
    assert response.status_code == 200


def test_tutorial_route(test_client): # noqa
    """
    Test the tutorial route to ensure it returns a status code of 200.
    """
    response = test_client.get("/tutorial")
    assert response.status_code == 200


def test_game_route(test_client):
    """
    Test the game route to ensure it returns a status code of 200.
    """
    response = test_client.get("/game")
    assert response.status_code == 200


def test_stats_route(test_client, mocker):
    """
    Test the stats route to ensure it returns a status code of 200.
    Mock the MongoDB collection to simulate the stats.
    """
    # Mock the count_documents method for MongoDB
    mocker.patch("app.GAME_RESULTS_COLLECTION.count_documents", return_value=5)

    response = test_client.get("/stats")
    assert response.status_code == 200
    assert b"user_wins" in response.data


def test_data_route(test_client):
    """
    Test the JSON data API to ensure it returns a success status and includes a data key.
    """
    response = test_client.get("/data")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert "data" in json_data


def test_test_db_route(test_client, mocker):
    """
    Test the MongoDB connection route to verify success or error status.
    Mock the database connection to test this functionality.
    """
    # Mock the insert_one method for MongoDB
    mocker.patch("app.GAME_RESULTS_COLLECTION.insert_one", return_value=None)
    # Mock the list_database_names method
    mocker.patch("app.client.list_database_names", return_value=["admin", "local", "test"])

    response = test_client.get("/test-db")
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"


def test_save_game_result(test_client, mocker):
    """
    Test the save_game_result route to ensure it correctly saves a game result.
    """
    # Mock the insert_one method for MongoDB
    mocker.patch("app.GAME_RESULTS_COLLECTION.insert_one", return_value=None)

    payload = {
        "user_choice": "rock",
        "computer_choice": "scissors",
        "winner": "User",
    }
    response = test_client.post("/save_game_result", json=payload)
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert json_data["message"] == "Game result saved"


def test_classify(test_client, mocker):
    """
    Test the classify route to ensure it returns classification results.
    Mock external API calls and MongoDB insertion.
    """
    # Mock requests.post for preprocessing and classification
    mocker.patch("requests.post", side_effect=[
        # Mock preprocess response
        type("Response", (), {"status_code": 200, "json": lambda: {"image_array": [1, 2, 3]}})(),
        # Mock classify response
        type("Response", (), {"status_code": 200, "json": lambda: {"result": "rock"}})()
    ])
    # Mock MongoDB insert_one
    mocker.patch("app.GAME_RESULTS_COLLECTION.insert_one", return_value=None)

    # Simulate an image upload
    response = test_client.post("/classify", data={"image": (b"fake_image_data", "test.png")})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["user_choice"] == "rock"
    assert "computer_choice" in json_data
    assert "result" in json_data


def test_simulate_computer_choice():
    """
    Test simulate_computer_choice to ensure it returns valid choices.
    """
    valid_choices = ["rock", "paper", "scissors"]
    for _ in range(100):
        choice = simulate_computer_choice()
        assert choice in valid_choices


def test_determine_result():
    """
    Test determine_result to ensure it correctly calculates the winner.
    """
    assert determine_result("rock", "scissors") == "User"
    assert determine_result("scissors", "paper") == "User"
    assert determine_result("paper", "rock") == "User"

    assert determine_result("rock", "rock") == "Nobody"
    assert determine_result("paper", "paper") == "Nobody"
    assert determine_result("scissors", "scissors") == "Nobody"

    assert determine_result("rock", "paper") == "Computer"
    assert determine_result("paper", "scissors") == "Computer"
    assert determine_result("scissors", "rock") == "Computer"

