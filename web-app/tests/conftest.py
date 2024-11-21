"""
Pytest configuration and fixtures for the Flask web application.
"""

import pytest
from ..app import app as flask_app, db  # Ensure app module is discoverable


@pytest.fixture(name="test_app")
def fixture_app():
    """
    Provide a Flask app instance with a test database configuration.
    """
    flask_app.config.update(
        {
            "TESTING": True,
            "DEBUG": False,
            "MONGO_DBNAME": "test_database",  # Use a separate test database
        }
    )
    yield flask_app

    # Clean up test data after tests are executed
    db.users.delete_many({})
    db.mouse_activity.delete_many({})
    db.sessions.delete_many({})


@pytest.fixture(name="test_client")
def fixture_client(test_app):
    """
    Provide a test client for the Flask app.
    """
    with test_app.test_client() as client:
        yield client
