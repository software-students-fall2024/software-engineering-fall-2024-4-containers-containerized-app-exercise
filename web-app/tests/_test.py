"""
This module contains unit tests for the application.
"""

import pytest

from app import create_app


@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client

def test_root1(client):
    """Test the / route on GET req"""
    response = client.get("/")
    html_text = response.data.decode('utf-8')
    assert "Start Recording" in html_text
    assert response.status_code == 200

def test_root2(client):
    """Test the / route on GET req"""
    response = client.get("/")
    html_text = response.data.decode('utf-8')
    assert "Waiting for permission to access the microphone..." in html_text
    assert response.status_code == 200

def test_404(client):
    """Test a non-existent route, expecting 404 error"""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
