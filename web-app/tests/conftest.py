"""
Configuring the webapp tests
"""

import pytest

#pylint: disable=import-error
from src.app import app


@pytest.fixture
def test_client():
    """Configuration"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
