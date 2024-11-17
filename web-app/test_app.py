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
    with app.test_client() as client:  # Use 'with' to ensure proper cleanup
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
    response = client.post('/api/detect')  # Use POST method here
    assert response.status_code == 200
    assert 'objects' in response.json  # Check if 'objects' is a key in the JSON response
