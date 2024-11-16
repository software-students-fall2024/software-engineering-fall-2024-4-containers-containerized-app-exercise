"""
This module contains tests for the Web App. Run with 'python -m pytest test_app.py' 
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import app  # Import the Flask app directly from app.py

# Fixture to create a test client
@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:  # Use a context manager to properly handle the client
        yield test_client  # This will return the test client to the test functions

def test_index_page(client):
    """Test the index page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Real-Time Object Detection' in response.data

def test_data_route(client):
    """Test the /data route."""
    response = client.get('/data')
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Should return a list of objects from MongoDB
