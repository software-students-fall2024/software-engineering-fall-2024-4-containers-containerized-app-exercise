"""
This module contains tests for the Web App. Run with 'python -m pytest test_app.py'
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import app

@pytest.fixture
def test_client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    # Use 'test_client' inside the fixture to avoid confusion
    with app.test_client() as test_client:  
        yield test_client  # This will return the test client to the test functions

def test_index_page(test_client):  # Use 'test_client' to avoid redefining 'client'
    """Test the index page route."""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Real-Time Object Detection' in response.data

def test_dashboard_page(test_client):  # Use 'test_client' to avoid redefining 'client'
    """Test the dashboard page."""
    response = test_client.get('/dashboard')  # Ensure this route exists
    assert response.status_code == 200
    assert b'Object Detection Trends' in response.data

def test_api_detect(test_client):  # Use 'test_client' to avoid redefining 'client'
    """Test the object detection API endpoint."""
    response = test_client.post('/api/detect')  # Ensure this route exists
    assert response.status_code == 200
    assert 'objects' in response.json  # Check if 'objects' is a key in the JSON response
    assert isinstance(response.json['objects'], list)  # Optionally, check that 'objects' is a list
    assert len(response.json['objects']) == 0  # You can also check that the list is empty
