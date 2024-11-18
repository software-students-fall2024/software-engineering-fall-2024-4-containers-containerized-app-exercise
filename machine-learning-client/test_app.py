import os
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["boyfriend_db"]
collection = db["focus_data"]

@pytest.fixture
def setup_test_data():
    collection.delete_many({"email": {"$regex": "test_user.*@example.com"}})
    yield
    collection.delete_many({"email": {"$regex": "test_user.*@example.com"}})

def test_insert_user(setup_test_data):
    result = collection.insert_one({"name": "Toshi", "email": "test_user@example.com"})
    assert result.inserted_id is not None

def test_get_user_by_email(setup_test_data):
    collection.insert_one({"name": "Toshi", "email": "test_user@example.com"})
    user = collection.find_one({"email": "test_user@example.com"})
    assert user is not None
    assert user["name"] == "Toshi"
    assert user["email"] == "test_user@example.com"