from pymongo import MongoClient
from datetime import datetime
import os


class DatabaseHandler:
    def __init__(self):
        self.client = MongoClient(
            host=os.environ.get("MONGODB_HOST", "localhost"),
            port=int(os.environ.get("MONGODB_PORT", 27017)),
            username=os.environ.get("MONGODB_USERNAME", "admin"),
            password=os.environ.get("MONGODB_PASSWORD", "password"),
        )
        self.db = self.client[os.environ.get("MONGODB_DATABASE", "emotion_detection")]

    def save_detection_result(self, image_id, emotions):
        """
        Save emotion detection results to database

        Args:
            image_id: Unique identifier for the image
            emotions: Dictionary containing detected emotions
        """
        collection = self.db.detection_results

        document = {
            "image_id": image_id,
            "emotions": emotions,
            "timestamp": datetime.utcnow(),
        }

        return collection.insert_one(document)
