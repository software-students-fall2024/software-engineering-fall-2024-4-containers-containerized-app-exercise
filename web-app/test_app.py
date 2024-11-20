# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

import pytest
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from io import BytesIO
from app import app, generate_stats_doc, retry_request

# Fixtures
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Tests for generate_stats_doc
@patch('app.collection')
def test_generate_stats_doc(mock_collection):
    mock_inserted_id = ObjectId()
    mock_collection.insert_one.return_value.inserted_id = mock_inserted_id

    _id = generate_stats_doc()

    mock_collection.insert_one.assert_called_once()
    assert _id == str(mock_inserted_id)

# Tests for retry_request
@patch('app.requests.post')
def test_retry_request_success_on_first_try(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files)
    assert response == mock_response
    mock_post.assert_called_once()

@patch('app.requests.post')
def test_retry_request_success_after_retries(mock_post):
    # Simulate exceptions on the first two attempts, then a successful response
    mock_post.side_effect = [
        Exception("Connection error"),
        Exception("Timeout"),
        MagicMock()
    ]

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response is not None
    assert mock_post.call_count == 3

@patch('app.requests.post')
def test_retry_request_all_failures(mock_post):
    # Simulate exceptions on all attempts
    mock_post.side_effect = Exception("Connection error")

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response is None
    assert mock_post.call_count == 3

# Tests for routes
@patch('app.generate_stats_doc', return_value=str(ObjectId()))
def test_home_route(mock_generate_stats_doc, client):
    response = client.get('/')
    assert response.status_code == 200
    assert "db_object_id" in response.headers['Set-Cookie']

@patch('app.generate_stats_doc', return_value=str(ObjectId()))
def test_home_route_with_existing_cookie(mock_generate_stats_doc, client):
    client.set_cookie('db_object_id', str(ObjectId()))
    response = client.get('/')
    assert response.status_code == 200

@patch('app.generate_stats_doc', return_value=str(ObjectId()))
def test_index_route(mock_generate_stats_doc, client):
    response = client.get('/index')
    assert response.status_code == 200

@patch('app.collection')
@patch('app.generate_stats_doc', return_value=str(ObjectId()))
def test_statistics_route(mock_generate_stats_doc, mock_collection, client):
    stats = {
        "Rock": {"wins": 1, "losses": 0, "ties": 0, "total": 1},
        "Paper": {"wins": 0, "losses": 1, "ties": 0, "total": 1},
        "Scissors": {"wins": 0, "losses": 0, "ties": 1, "total": 1},
        "Totals": {"wins": 1, "losses": 1, "ties": 1},
    }
    mock_collection.find_one.return_value = stats

    response = client.get('/statistics')
    assert response.status_code == 200
    assert b"Statistics" in response.data

@patch('app.retry_request')
@patch('app.collection.update_one')
def test_result_route_success(mock_update_one, mock_retry_request, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Rock"}
    mock_retry_request.return_value = mock_response

    mock_id = ObjectId()
    client.set_cookie('db_object_id', str(mock_id))

    data = {'image': (BytesIO(b"fake image data"), 'test_image.jpg')}
    response = client.post('/result', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b"AI wins!" in response.data

@patch('app.retry_request')
def test_result_route_unknown_gesture(mock_retry_request, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Unknown"}
    mock_retry_request.return_value = mock_response

    mock_id = ObjectId()
    client.set_cookie('db_object_id', str(mock_id))

    data = {'image': (BytesIO(b"fake image data"), 'test_image.jpg')}
    response = client.post('/result', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b"Gesture not recognized" in response.data

@patch('app.retry_request')
def test_result_route_ml_failure(mock_retry_request, client):
    mock_retry_request.return_value = None

    mock_id = ObjectId()
    client.set_cookie('db_object_id', str(mock_id))

    data = {'image': (BytesIO(b"fake image data"), 'test_image.jpg')}
    response = client.post('/result', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b"No valid prediction" in response.data

@patch('app.retry_request')
def test_result_route_no_image(mock_retry_request, client):
    response = client.post('/result', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No image file provided" in response.data


