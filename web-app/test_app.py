"""
This module contains tests for the Web App. Run with 'python -m pytest test_app.py' 
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import app  # Import the Flask app directly from app.py

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    client = app.test_client()  # Create a test client
    yield client  # This will return the test client to the test functions

def test_index_page(client):
    """Test the index page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Real-Time Object Detection' in response.data  # Update this to match your HTML content

def test_dashboard_page(client):
    """Test the dashboard page."""
    response = client.get('/dashboard')  # Ensure this route exists in your app
    assert response.status_code == 200
    assert b'Object Detection Trends' in response.data  # Update to match the content

def test_api_detect(client):
    """Test the object detection API endpoint."""
    response = client.get('/api/detect')  # Ensure this route exists and is correct
    assert response.status_code == 200
    assert b'objects' in response.json  # Ensure 'objects' is in the JSON response
