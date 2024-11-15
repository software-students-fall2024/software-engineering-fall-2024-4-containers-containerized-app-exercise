"""
Configuration settings for the web application.
This module contains all configuration classes and settings.
"""

class Config:  # pylint: disable=too-few-public-methods
    """Application configuration class."""
    SECRET_KEY = 'your-secret-key'
    MONGO_URI = 'mongodb://localhost:27017/emotion_detection'
