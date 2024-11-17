"""
Configuration settings for the web application.
This module contains all configuration classes and settings.
"""
import os

class Config:  # pylint: disable=too-few-public-methods
    """Application configuration class."""

    SECRET_KEY = "your-secret-key"
    MONGO_URI = f"mongodb://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@{os.getenv('MONGODB_HOST')}:{os.getenv('MONGODB_PORT')}/{os.getenv('MONGODB_DATABASE')}"
