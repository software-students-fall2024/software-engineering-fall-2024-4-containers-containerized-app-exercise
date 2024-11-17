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

    def save_detection_result(self, image_id, emotions, user_id=None):
        """
        Save emotion detection results to database

        Args:
            image_id: Unique identifier for the image
            emotions: Dictionary containing detected emotions
            user_id: Optional user identifier
        """
        collection = self.db.detection_results

        document = {
            "image_id": image_id,
            "emotions": emotions,
            "timestamp": datetime.utcnow(),
        }
        
        if user_id:
            document["user_id"] = user_id

        return collection.insert_one(document)

    def get_detection_result(self, image_id):
        """
        Get emotion detection results from database by image_id

        Args:
            image_id: Unique identifier for the image

        Returns:
            dict: Detection results or None if not found
        """
        collection = self.db.detection_results
        result = collection.find_one({"image_id": image_id})
        
        if result:
            # Convert ObjectId to string for JSON serialization
            result['_id'] = str(result['_id'])
            return result
        return None
