# test_client.py
# cd machine-learning-client
# pytest test_client.py -v
# pytest -v

import os
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from client import app, collection

# Fixture to create a test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test successful prediction
@patch('client.rf_client')
@patch('client.collection')
def test_predict_success(mock_collection, mock_rf_client, client):
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [
            {"class": "Rock", "confidence": 0.95}
        ]
    }
    
    # Mock the insert_one method
    mock_collection.insert_one.return_value = MagicMock()

    # Create a dummy image file
    data = {
        'image': (BytesIO(b"fake image data"), 'test_image.jpg')
    }

    response = client.post('/predict', content_type='multipart/form-data', data=data)
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['gesture'] == "Rock"
    assert json_data['confidence'] == 0.95

    # Ensure infer was called with the correct image path
    mock_rf_client.infer.assert_called_once()
    
    # Ensure data was inserted into MongoDB
    mock_collection.insert_one.assert_called_once()

# Test prediction with no image provided
def test_predict_no_image(client):
    response = client.post('/predict', content_type='multipart/form-data', data={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "No image file provided"

# Test inference API failure
@patch('client.rf_client')
def test_predict_inference_failure(mock_rf_client, client):
    # Simulate an inference API failure
    mock_rf_client.infer.side_effect = Exception("Inference API error")

    data = {
        'image': (BytesIO(b"fake image data"), 'test_image.jpg')
    }

    response = client.post('/predict', content_type='multipart/form-data', data=data)
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data['error']

# Test MongoDB insertion failure
@patch('client.rf_client')
@patch('client.collection')
def test_predict_mongodb_failure(mock_collection, mock_rf_client, client):
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [
            {"class": "Paper", "confidence": 0.85}
        ]
    }
    
    # Simulate a MongoDB insertion failure
    mock_collection.insert_one.side_effect = Exception("MongoDB insertion error")

    data = {
        'image': (BytesIO(b"fake image data"), 'test_image.jpg')
    }

    response = client.post('/predict', content_type='multipart/form-data', data=data)
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data['error']

# Test invalid image path (FileNotFoundError)
@patch('client.rf_client')
@patch('client.collection')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('client.os.path.exists', return_value=False)
def test_predict_file_not_found(mock_os_path_exists, mock_makedirs, mock_collection, mock_rf_client, client):
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [
            {"class": "Scissors", "confidence": 0.90}
        ]
    }
    
    # Simulate a FileNotFoundError during file saving
    with patch('client.request.files') as mock_request_files:
        mock_request_files.__contains__.return_value = True
        mock_request_files.__getitem__.return_value.save.side_effect = FileNotFoundError("File not found")
        
        data = {
            'image': (BytesIO(b"fake image data"), 'test_image.jpg')
        }

        response = client.post('/predict', content_type='multipart/form-data', data=data)
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert "Prediction error" in json_data['error']

# Test invalid JSON response from inference API
@patch('client.rf_client')
@patch('client.collection')
def test_predict_invalid_inference_response(mock_collection, mock_rf_client, client):
    # Mock the inference result with missing 'class' key
    mock_rf_client.infer.return_value = {
        "predictions": [
            {"confidence": 0.80}
        ]
    }

    data = {
        'image': (BytesIO(b"fake image data"), 'test_image.jpg')
    }

    response = client.post('/predict', content_type='multipart/form-data', data=data)
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['gesture'] == "Unknown"
    assert json_data['confidence'] == 0

