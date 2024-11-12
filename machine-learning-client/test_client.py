import pytest
import requests
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime
from client_code import get_camera_data, fetch_image, detect_vehicles, save_to_db

# Test for get_cpip install pytest pytest-cov

@patch('requests.get')
def test_get_camera_data(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'ID': '123', 'Name': 'Test Camera', 'Url': 'http://example.com/test.jpg'}]
    mock_get.return_value = mock_response

    data = get_camera_data()
    assert data is not None
    assert data[0]['ID'] == '123'
    assert data[0]['Name'] == 'Test Camera'

# Test for fetch_image
@patch('requests.get')
def test_fetch_image(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = cv2.imencode('.jpg', np.zeros((10, 10, 3), dtype=np.uint8))[1].tobytes()
    mock_get.return_value = mock_response

    img = fetch_image("http://example.com/test.jpg")
    assert img is not None
    assert isinstance(img, np.ndarray)

# Test for detect_vehicles
def test_detect_vehicles():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    vehicle_count = detect_vehicles(img)
    assert vehicle_count == 0  # Placeholder, should adjust based on actual detection logic

# Test for save_to_db
@patch('client_code.traffic_data_collection.insert_one')
def test_save_to_db(mock_insert):
    vehicle_count = 5
    camera_info = {'ID': '123', 'Name': 'Test Camera'}
    
    save_to_db(vehicle_count, camera_info)
    data = {
        "timestamp": datetime.utcnow(),
        "vehicle_count": vehicle_count,
        "camera_id": camera_info['ID'],
        "location": camera_info['Name']
    }
    mock_insert.assert_called_once_with(data)
