"""
This module contains tests for the machine learning client.
"""

from os import getenv
import pytest

def test_env():
    """
    Tests the retrieval of required environment variables.
    Fails if any of the required variables are not set.
    """
    mongodb_uri = getenv("MONGODB_URI")
    mongodb_username = getenv("MONGODB_USERNAME")
    mongodb_password = getenv("MONGODB_PASSWORD")

    if mongodb_uri is None:
        pytest.fail("Could not retrieve MONGODB_URI")
    if mongodb_username is None:
        pytest.fail("Could not retrieve MONGODB_USERNAME")
    if mongodb_password is None:
        pytest.fail("Could not retrieve MONGODB_PASSWORD")
