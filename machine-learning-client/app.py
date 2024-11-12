"""
This module is the main entry point for the machine learning client, connecting
to MongoDB and serving as the backend API for the client.
"""

from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["financiersDB"]
