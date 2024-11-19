"""
Flask application for MongoDB operations in the boyfriend client.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["boyfriend_db"]
collection = db["focus_data"]