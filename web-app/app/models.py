from pymongo import MongoClient
from datetime import datetime

class Database:
    def __init__(self):
        # 连接到MongoDB数据库
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client.emotion_detection

    def get_latest_results(self, limit=10):
        try:
            results = list(self.db.results.find().sort('timestamp', -1).limit(limit))
            return results
        except Exception as e:
            print(f"Error getting results: {e}")
            return []

    def save_result(self, image_url, emotion, confidence):
        try:
            result = {
                'timestamp': datetime.now(),
                'image_url': image_url,
                'emotion': emotion,
                'confidence': confidence
            }
            self.db.results.insert_one(result)
            return True
        except Exception as e:
            print(f"Error saving result: {e}")
            return False
