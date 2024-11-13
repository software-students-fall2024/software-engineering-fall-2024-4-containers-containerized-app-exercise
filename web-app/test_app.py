"""
Unit tests for app.py web app.
"""

import pytest
from app import launch_app


@pytest.fixture
def app_client():
    """Create a test client for the Flask app."""
    app = launch_app()
    with app.test_client() as client:
        yield client


def test_index_route(app_client):
    """Test the index route."""
    response = app_client.get("/")
    assert response.status_code == 200
    assert b"Tap to Listen" in response.data


# If we use `/results`
# def test_results_route(client):
#     """Test the results route."""
#     response = client.get("/results")
#     assert response.status_code == 200
#     assert b"Classification Result" in response.data
