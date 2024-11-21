import pytest
import sys
import os

# Add the directory containing `app.py` to the Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from app import app as flask_app, db


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "DEBUG": False,
            "MONGO_DBNAME": "test_database",  # Use a separate test database
        }
    )
    yield flask_app
    # Clean up test data
    db.users.delete_many({})
    db.mouse_activity.delete_many({})
    db.sessions.delete_many({})


@pytest.fixture
def client(app):
    """Provide a test client for the Flask app."""
    with app.test_client() as client:
        yield client
