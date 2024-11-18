import pytest
from unittest.mock import patch, MagicMock
from flask import json
from app import app, process_image, base64ToNumpy
from bson import ObjectId
import base64

# Example mock data
mock_image_data = {"_id": ObjectId("507f1f77bcf86cd799439011"), "image_data": b"mock_image_data"}
mock_output = ["mock_output"]
mock_label = "mock_label"

# Mocking the process_image function
def mock_process_image(image_data):
    return mock_output, mock_label


@pytest.fixture
def client():
    """
    Creates a test client for the Flask app.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_process_image_1(client):
    """
    Test the process_image function.
    """
    image_path = "./images/test_image_1.jpg"
    with open(image_path, "rb") as image_file:
        image = base64.b64encode(image_file.read()).decode("utf-8")
        
    result = process_image(image)
    assert result[1] == "Yes , we won.", "Expected translation to be 'Yes , we won.'"
    
def test_process_image_2(client):
    """
    Test the process_image function.
    """
    image_path = "./images/test_image_2.jpg"
    with open(image_path, "rb") as image_file:
        image = base64.b64encode(image_file.read()).decode("utf-8")
        
    result = process_image(image)
    assert result[1] == "Perfect , You did  a great job.", "Expected translation to be 'Perfect , You did  a great job.'"
    
    


def test_process_image_invalid_request(client):
    """
    Test the /processImage endpoint
    """

    response = app.test_client().post("/processImage", json={})
    assert response.status_code in (200, 400)

