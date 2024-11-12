"""
This application serves as the main entry point for the machine learning client,
connecting to MongoDB and performing data analysis tasks.
"""

from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["financiersDB"]
