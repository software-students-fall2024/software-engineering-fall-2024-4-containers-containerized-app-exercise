"""
This module contains tests for environment variable retrieval.
"""

from os import getenv
import pytest


def test_env():
    """
    Tests the retrieval of required environment variables.
    Fails if any of the required variables are not set.
    """
    connstr = getenv("DB_URI")
    key = getenv("SECRET")

    if connstr is None:
        pytest.fail("Could not retrieve DB_URI")
    if key is None:
        pytest.fail("Could not retrieve flask secret")
