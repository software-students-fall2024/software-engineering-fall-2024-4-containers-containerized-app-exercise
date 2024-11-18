"""
Unit tests for MongoDB operations in the boyfriend client.
"""

import pytest
from app import collection


@pytest.fixture
def clear_test_data():
    """
    Clean up test data before and after tests.
    """
    collection.delete_many({"email": {"$regex": "test_user.*@example.com"}})
    yield
    collection.delete_many({"email": {"$regex": "test_user.*@example.com"}})


def test_mongodb_connection(_clear_test_data):
    """
    Test MongoDB setup and insert operation.
    """
    result = collection.insert_one({"name": "Toshi", "email": "test_user@example.com"})
    assert result.inserted_id is not None
    user = collection.find_one({"email": "test_user@example.com"})
    assert user is not None
    assert user["name"] == "Toshi"
    assert user["email"] == "test_user@example.com"
