"""
This module contains unit tests for the application.
"""

import pytest

from app import create_app


# TEST
def test_function():
    """ sample test """
    assert True

@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client
