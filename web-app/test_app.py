"""
Unit tests for app.py web app.
"""

import pytest


@pytest.fixture
def app_client(app):
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Tap to Listen" in response.data


# If we use `/results`
# def test_results_route(client):
#     """Test the results route."""
#     response = client.get("/results")
#     assert response.status_code == 200
#     assert b"Classification Result" in response.data
