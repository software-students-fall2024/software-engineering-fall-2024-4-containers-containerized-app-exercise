"""
Database models and operations module.
This module handles all database interactions for the emotion detection system.
"""

from datetime import datetime
from pymongo import MongoClient
import requests
import os


class Database:
    """Handles all database operations for the emotion detection system."""

    def __init__(self):
        """Initialize database connection."""
        username = os.environ.get('MONGODB_USERNAME', 'admin')
        password = os.environ.get('MONGODB_PASSWORD', 'password')
        host = os.environ.get('MONGODB_HOST', 'localhost')
        port = os.environ.get('MONGODB_PORT', '27017')
        
        # Create connection URL with authentication
        connection_string = f"mongodb://{username}:{password}@{host}:{port}"
        
        # Connect to MongoDB with authentication
        self.client = MongoClient(connection_string)
        self.db = self.client.emotion_detection

    def get_latest_results(self, user_id, limit=10):
        """
        Retrieve the latest emotion detection results for a specific user.

        Args:
            user_id (str): Email of the user
            limit (int): Maximum number of results to return

        Returns:
            list: List of detection results for the user
        """
        try:
            results = list(self.db.detection_results.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
            return results
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error getting results: {e}")
            return []

    def find_user(self, query):
        """Find a user in the database"""
        return self.db.users.find_one(query)

    def add_user(self, user_data):
        """Add a new user to the database"""
        return self.db.users.insert_one(user_data)

    def get_emotion_detection(self, image_id):
        """
        Call emotion detection service with image ID.

        Args:
            image_id (str): ID of the saved picture

        Returns:
            str: Detection result or None if failed
        """
        try:
            response = requests.get(f"http://localhost:5001/get-detection/{image_id}")
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error calling detection service: {e}")
            return None

    def save_picture(self, user_id, image_data):
        """
        Save an image to the pictures collection and get emotion detection.

        Args:
            user_id (str): Email of the user
            image_data (bytes): Binary image data

        Returns:
            detection_result_id (str): mood result id of detection
        """
        try:
            pic_doc = {
                "user_id": user_id,
                "image": image_data,
                "timestamp": datetime.now()
            }
            result = self.db.pictures.insert_one(pic_doc)
            pic_id = str(result.inserted_id)
        
            # Get emotion detection result
            detection_result_id = self.get_emotion_detection(pic_id)
            return detection_result_id
            
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error saving picture: {e}")
            return None

    def get_detection_result(self, detection_result_id):
        """
        Retrieve the detection result record by its ID.

        Args:
            detection_result_id (str): ID of the detection result

        Returns:
            dict: Detection result document or None if not found
        """
        try:
            result = self.db.detection_results.find_one({"_id": detection_result_id})
            return result
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error getting detection result: {e}")
            return None
