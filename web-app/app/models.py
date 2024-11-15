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
        self.client = MongoClient("mongodb://localhost:27017/")
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
