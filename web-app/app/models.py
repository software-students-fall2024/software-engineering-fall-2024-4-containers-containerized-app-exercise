"""
Database models and operations module.
This module handles all database interactions for the emotion detection system.
"""

from datetime import datetime
from pymongo import MongoClient


class Database:
    """Handles all database operations for the emotion detection system."""

    def __init__(self):
        """Initialize database connection."""
        username = "admin"
        password = "password"
        host = "192.168.80.130"
        port = 27017
        
        # Create connection URL with authentication
        connection_string = f"mongodb://{username}:{password}@{host}:{port}"
        
        # Connect to MongoDB with authentication
        self.client = MongoClient(connection_string)
        self.db = self.client.emotion_detection

    def get_latest_results(self, limit=10):
        """
        Retrieve the latest emotion detection results.

        Args:
            limit (int): Maximum number of results to return

        Returns:
            list: List of detection results
        """
        try:
            results = list(self.db.results.find().sort("timestamp", -1).limit(limit))
            return results
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error getting results: {e}")
            return []

    def save_result(self, image_url, emotion, confidence):
        """
        Save a new emotion detection result.

        Args:
            image_url (str): URL of the processed image
            emotion (str): Detected emotion
            confidence (float): Confidence score

        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            result = {
                "timestamp": datetime.now(),
                "image_url": image_url,
                "emotion": emotion,
                "confidence": confidence,
            }
            self.db.results.insert_one(result)
            return True
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error saving result: {e}")
            return False

    def find_user(self, query):
        """Find a user in the database"""
        return self.db.users.find_one(query)

    def add_user(self, user_data):
        """Add a new user to the database"""
        return self.db.users.insert_one(user_data)

    def save_picture(self, user_id, image_data):
        """
        Save an image to the pictures collection.

        Args:
            user_id (str): Email of the user
            image_data (bytes): Binary image data

        Returns:
            str: ID of the saved picture
        """
        try:
            pic_doc = {
                "user_id": user_id,
                "image": image_data,
                "timestamp": datetime.now()
            }
            result = self.db.pictures.insert_one(pic_doc)
            return str(result.inserted_id)
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error saving picture: {e}")
            return None
