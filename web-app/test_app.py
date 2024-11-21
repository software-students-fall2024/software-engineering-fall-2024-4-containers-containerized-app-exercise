"""
Tests for app.py, the web app for the Plant Identifier project.
This script tests each route independently to achieve a minimum of 80% code coverage.
"""

import os
import pytest
import pymongo
from werkzeug.security import generate_password_hash
from app import create_app


@pytest.fixture(scope="module")
def app():
    """
    Fixture to create and configure a new app instance for each test module.
    """
    # Initialize the Flask app with test configuration
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "MONGO_TEST_DBNAME": os.getenv("MONGO_TEST_DBNAME", "plant_identifier_test")
    }
    test_app = create_app()
    test_app.debug = True

    # Connect to the test MongoDB instance
    connection = pymongo.MongoClient(test_config["MONGO_URI"])
    test_app.db = connection[test_config["MONGO_TEST_DBNAME"]]

    # Clear collections before tests
    for collection in test_app.db.list_collection_names():
        test_app.db.drop_collection(collection)

    yield test_app

    # Teardown: Drop the test database after tests
    connection.drop_database(test_config["MONGO_TEST_DBNAME"])
    connection.close()


@pytest.fixture(scope="module")
def client(app):
    """
    Fixture to provide a test client for the Flask app.
    """
    return app.test_client()


@pytest.fixture(scope="module")
def runner(app):
    """
    Fixture to provide a CLI runner for the Flask app.
    """
    return app.test_cli_runner()


def test_home_without_user(client):
    """Test the home page route without any user input."""
    response = client.get("/")
    assert response.status_code == 200
    # Test for a specific string that's only in the template for this route
    assert b"to get started!" in response.data


def test_home_with_user(client, app):
    """Test the home route with user input."""
    # Insert mock plant entries into the test database
    app.db.plants.insert_many([
        {"_id": "1", "photo": "photo1", "name": "rose", "user": "test_user"},
        {"_id": "2", "photo": "photo2", "name": "lily", "user": "test_user"},
    ])
    response = client.get("/?user=test_user")
    assert response.status_code == 200
    assert b"rose" in response.data
    assert b"lily" in response.data


def test_login_post(client, app):
    """Test that the login form posts correctly."""
    # Insert a test user into the test database
    app.db.users.insert_one({
        "username": "test_user",
        "password": generate_password_hash("secure_password")
    })

    response = client.post("/login", data={
        "username": "test_user",
        "password": "secure_password"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/?user=test_user"


def test_signup_post(client, app):
    """Test that the signup form posts correctly."""
    response = client.post("/signup", data={
        "username": "new_user",
        "password": "pass"
    })
    assert response.status_code == 302
    assert response.headers["Location"] == "/?user=new_user"

    # Make sure the new user was added properly to the database
    user = app.db.users.find_one({"username": "new_user"})
    assert user is not None
    assert user["username"] == "new_user"


def test_upload_post(client, app):
    """Test that a new entry photo uploads correctly."""
    # Ensure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"

    # Make a mock photo data
    photo_data = "data:image/jpeg;base64,encodedphoto"

    response = client.post("/upload", data={"photo": photo_data})
    assert response.status_code == 302

    # Make sure this entry was created and the photo was added correctly
    plant = app.db.plants.find_one({"photo": photo_data})
    assert plant is not None
    assert plant["name"] == "Plant"


def test_new_entry_post(client, app):
    """Test that adding instructions to a new entry works correctly."""
    # Ensure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"

    # Insert a mock plant entry
    plant_id = app.db.plants.insert_one({
        "photo": "data:image/jpeg;base64,encodedphoto",
        "name": "Plant"
    }).inserted_id

    response = client.post(
        f"/new_entry?new_entry_id={plant_id}",
        data={"instructions": "Water daily"}
    )
    assert response.status_code == 302

    # Make sure this entry exists and the instructions were added correctly
    plant = app.db.plants.find_one({"_id": plant_id})
    assert plant is not None
    assert plant.get("instructions") == "Water daily"


def test_history(client, app):
    """Test that the history route displays past entries correctly."""
    # Insert mock plant entries into the test database
    app.db.plants.insert_many([
        {"name": "cactus", "photo": "Photo1", "user": "test_user"},
        {"name": "oak tree", "photo": "Photo2", "user": "test_user"},
    ])

    # Ensure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"

    response = client.get("/history")
    assert response.status_code == 200
    assert b"cactus" in response.data
    assert b"oak tree" in response.data
    