"""
This module establishes a connection to MongoDB using pymongo.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")

# Establish a MongoDB client
client = MongoClient(MONGODB_URI)

db = client["Its_over_again_database"]
