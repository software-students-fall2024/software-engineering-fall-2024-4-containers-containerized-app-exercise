"""
This module contains tests for the ML client. Run with 'python -m pytest test_app.py' 
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import create_app  # Make sure this is correctly imported from your app

# Fixture to create a test client
@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app = create_app()  # Assuming you have a factory function that creates your app
    app.config['TESTING'] = True
    client = app.test_client()  # Create a test client
    yield client  # This will return the test client to the test functions

def test_index_page(client):
    """Test the index page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Real-Time Object Detection' in response.data

def test_dashboard_page(client):
    """Test the dashboard page."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Object Detection Trends' in response.data

def test_api_detect(client):
    """Test the object detection API endpoint."""
    response = client.get('/api/detect')  # Assuming the endpoint exists
    assert response.status_code == 200
    assert b'objects' in response.json  # Ensure 'objects' is in the JSON response
