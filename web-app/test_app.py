import json
from unittest.mock import patch

# Test the index route
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Sentence Checker' in response.data

# Test the /checkSentiment route
@patch('app.collection.insert_one')
def test_submit_sentence(mock_insert, client):
    # Mock the insertion to prevent actual MongoDB interaction
    mock_insert.return_value.inserted_id = 'fake_id'
    
    data = {'sentence': "This is a test paragraph. It contains multiple sentences."}
    response = client.post('/checkSentiment', data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200
    response_data = response.get_json()
    assert 'request_id' in response_data
    assert isinstance(response_data['request_id'], str)

# Test the /checkSentiment route with an empty input
@patch('app.collection.insert_one')
def test_submit_sentence_empty(mock_insert, client):
    data = {'sentence': ""}
    response = client.post('/checkSentiment', data=json.dumps(data), content_type='application/json')

    assert response.status_code == 200
    response_data = response.get_json()
    assert 'request_id' in response_data
    assert isinstance(response_data['request_id'], str)

# Test the /get_analysis route
@patch('app.collection.find_one')
def test_get_analysis(mock_find, client):
    # Mock the document retrieval
    mock_find.return_value = {
        "_id": "fake_id",
        "request_id": "unique_request_id",
        "sentences": [
            {"sentence": "This is a test.", "status": "processed", "analysis": {"compound": 0.5}}
        ],
        "overall_status": "processed",
        "timestamp": "2024-11-16T04:20:00"
    }

    response = client.get('/get_analysis?request_id=unique_request_id')

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data['request_id'] == 'unique_request_id'
    assert response_data['overall_status'] == 'processed'

# Test the /get_analysis route for a missing request_id
@patch('app.collection.find_one')
def test_get_analysis_not_found(mock_find, client):
    # Mock the document not being found
    mock_find.return_value = None

    response = client.get('/get_analysis?request_id=missing_request_id')

    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data['message'] == "No processed analysis found"