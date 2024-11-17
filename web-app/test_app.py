"""
This module contains tests for the Web App. Run with 'python -m pytest test_app.py'
or to see with coverage run with 'python -m pytest --cov=app test_app.py'
"""

import pytest
from app import app

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:  # The fixture's name is 'client'
        yield client  # This will return the test client to the test functions

def test_index_page(client):  # Use 'client' as the argument name to match the fixture
    """Test the index page route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Real-Time Object Detection' in response.data

def test_dashboard_page(client):  # Use 'client' as the argument name
    """Test the dashboard page."""
    response = client.get('/dashboard')  # Ensure this route exists
    assert response.status_code == 200
    assert b'Object Detection Trends' in response.data

def test_api_detect(client):  # Use 'client' as the argument name
    """Test the object detection API endpoint."""
    response = client.post('/api/detect')  # Ensure this route exists
    assert response.status_code == 200
    assert 'objects' in response.json  # Check if 'objects' is a key in the JSON response
    assert isinstance(response.json['objects'], list)  # Optionally, check that 'objects' is a list
    assert len(response.json['objects']) == 0  # You can also check that the list is empty
