"""
Database models and operations module.
This module handles all database interactions for the emotion detection system.
"""

from datetime import datetime
from pymongo import MongoClient
import requests
import os
from bson.objectid import ObjectId


class Database:
    """Handles all database operations for the emotion detection system."""

    def __init__(self):
        """Initialize database connection."""
        username = os.environ.get('MONGODB_USERNAME', 'admin')
        password = os.environ.get('MONGODB_PASSWORD', 'password')
        host = os.environ.get('MONGODB_HOST', 'localhost')
        port = os.environ.get('MONGODB_PORT', '27017')
        
        # Create connection URL with authentication
        connection_string = f"mongodb://{username}:{password}@{host}:{port}/?authSource=admin"        
        # Connect to MongoDB with authentication
        self.client = MongoClient(connection_string)
        self.db = self.client.emotion_detection

    def get_latest_results(self, user_id, limit=5):
        """
        Get latest detection results for a user

        Args:
            user_id (str): User's email
            limit (int): Maximum number of results to return

        Returns:
            list: List of detection results
        """
        try:
            # 获取用户最近的图片记录
            pictures = self.db.pictures.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)

            results = []
            for pic in pictures:
                # 获取对应的情绪检测结果
                detection = self.db.detection_results.find_one({
                    "user_id": user_id,
                    "picture_id": str(pic["_id"])
                })
                
                if detection:
                    results.append({
                        'image_url': f'/images/{str(pic["_id"])}',
                        'emotion': detection['emotions'],
                        'timestamp': pic['timestamp']
                    })
                    
            return results
        except Exception as e:
            print(f"Error getting latest results: {e}")
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
            dict: Detection results or None if failed
        """
        try:
            # 保存图片到数据库
            pic_doc = {
                "user_id": user_id,
                "image": image_data,
                "timestamp": datetime.now()
            }
            result = self.db.pictures.insert_one(pic_doc)
            pic_id = str(result.inserted_id)

            # 调用 ML Client 的检测接口
            files = {'image': ('image.jpg', image_data, 'image/jpeg')}
            data = {'user_id': user_id}
            response = requests.post(
                'http://ml-client:5001/detect',
                files=files,
                data=data
            )

            if response.status_code == 200:
                detection_result = response.json()
                if detection_result['status'] == 'success':
                    # 保存检测结果到数据库
                    detection_doc = {
                        "user_id": user_id,
                        "picture_id": pic_id,
                        "emotions": detection_result['emotions'],
                        "timestamp": datetime.now()
                    }
                    self.db.detection_results.insert_one(detection_doc)
                    
                    return {
                        'image_url': f'/images/{pic_id}',
                        'emotion': detection_result['emotions']
                    }
            return None
            
        except Exception as e:
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

    def get_image(self, image_id):
        """
        Get image data from database by ID

        Args:
            image_id (str): ID of the image

        Returns:
            bytes: Image data or None if not found
        """
        try:
            result = self.db.pictures.find_one({'_id': ObjectId(image_id)})
            if result and 'image' in result:
                return result['image']
            return None
        except Exception as e:
            print(f"Error getting image: {e}")
            return None
