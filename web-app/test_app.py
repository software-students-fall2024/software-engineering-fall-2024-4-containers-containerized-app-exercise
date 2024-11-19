"""
Tests for app.py, the web app for this project
This script tests each route independently to achieve a minimum of 80% code coverage

"""
from unittest.mock import patch
import pytest
import mongomock
from flask import session
from app import create_app  # Update with your actual app file name

@pytest.fixture
def app():
    """
    Creates Flask application and Mongomock db for testing
    """
    # Mock the MongoDB client with an in-memory database (mongomock)
    with patch("app.pymongo.MongoClient", new=mongomock.MongoClient) as MockMongoClient:
        mock_client = mongomock.MongoClient()  # Use an in-memory MongoDB
        mock_db = mock_client["test_plantify"]  # Name of the in-memory test database

        # Replace the db attribute in the app with the mock database
        MockMongoClient.return_value = mock_client

        # Pass the test-specific configuration to the app factory
        app = create_app(
            test_config={
                "TESTING": True,
                "MONGO_URI": "mongodb://mock_uri:27017/test_plantify",
                "DB_CLIENT": mock_client,
            }
        )
        app.debug = True

        app.db = mock_db  # Attach the mock database to the app for testing

        return app


@pytest.fixture
def client(app):
    return app.test_client()

def test_home_without_user(client):
    """Test home page route without no user input yet"""
    response = client.get("/")
    assert response.status_code == 200
    # test for specific string that's only in the template for this route
    assert b"to get started!" in response.data

def test_home_with_user(client, app):
    """Test home route with user input"""
    app.db.plants.insert_many([
        {"_id": "1", "photo": "photo1", "name": "rose", "user": "test_user"},
        {"_id": "2", "photo": "photo2", "name": "lily", "user": "test_user"},
    ])
    response = client.get("/?user=test_user")
    assert response.status_code == 200
    assert b"rose" in response.data
    assert b"lily" in response.data

def test_login_post(client):
    """Test the login form results post correctly"""
    response = client.post("/login", data={"username": "test_user"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/?user=test_user"


def test_signup_post(client, app):
    """Test the signup form results post correctly"""
    response = client.post("/signup", data={"username": "new_user", "password": "pass"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/?user=new_user"
    # make sure new user was added properly to db
    user = app.db.users.find_one({"username": "new_user"})
    assert user is not None


def test_upload_post(client, app):
    """Test that a new entry photo uploads correctly"""
    # make sure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"
    # make a mock photo item that's consistent with the real db input
    photo_data = "data:image/jpeg;base64,encodedphoto"
    response = client.post("/upload", data={"photo": photo_data})
    assert response.status_code == 302
    # make sure this entry was created and the photo was added correctly
    plant = app.db.plants.find_one({"photo": photo_data})
    assert plant is not None
    


def test_new_entry_post(client, app):
    """Test that the rest of the new entry posts correctly"""
    # make sure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"
    plant_id = app.db.plants.insert_one({"photo": "data:image/jpeg;base64,encodedphoto", "name": "Plant"}).inserted_id
    response = client.post(f"/new_entry?new_entry_id={plant_id}", data={"instructions": "Water daily"})
    assert response.status_code == 302
    # make sure this entry exists and the instructions were added correctly
    plant = app.db.plants.find_one({"_id": plant_id})
    assert plant["instructions"] == "Water daily"


def test_history(client, app):
    """Test the past entries (history) route"""
    app.db.plants.insert_many([
        {"name": "cactus", "photo": "Photo1", "user": "test_user"},
        {"name": "oak tree", "photo": "Photo2", "user": "test_user"},
    ])
    # make sure the correct user is currently logged in
    with client.session_transaction() as session:
        session["username"] = "test_user"
    response = client.get("/history")
    assert response.status_code == 200
    assert b"cactus" in response.data
    assert b"oak tree" in response.data
