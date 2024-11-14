import pytest 
from os import getenv

def test_env():
    MONGODB_URI = getenv("MONGODB_URI")
    MONGODB_USERNAME = getenv("MONGODB_URI")
    MONGODB_PASSWORD = getenv("MONGODB_URI")

    if MONGODB_URI is None:
        pytest.fail("Could not retrieve MONGODB_URI")
    if MONGODB_USERNAME is None:
        pytest.fail("Could not retrieve MONGODB_USERNAME")
    if MONGODB_PASSWORD is None:
        pytest.fail("Could not retrieve MONGODB_PASSWORD")
