"""
Unit tests for app.py
"""
# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

# pylint web-app/
# black .

# Standard library imports
from io import BytesIO
from unittest.mock import patch, MagicMock

# Third party imports
import pytest
import requests
from bson.objectid import ObjectId

# Local application imports
from app import app, generate_stats_doc, retry_request


@pytest.fixture(name="test_client")
def fixture_client():
    """
    Test fixture that creates a Flask test client.

    Returns:
        FlaskClient: A test client for making requests to the Flask application
    """
    app.config["TESTING"] = True
    with app.test_client() as testing_client:
        yield testing_client


@patch("app.collection")
def test_generate_stats_doc(mock_collection):
    """
    Test the generation of a new statistics document in the database.

    Args:
        mock_collection: Mocked MongoDB collection object

    Verifies:
        - Document insertion is called once
        - Correct ObjectId is returned as string
    """
    mock_inserted_id = ObjectId()
    mock_collection.insert_one.return_value.inserted_id = mock_inserted_id

    _id = generate_stats_doc()

    mock_collection.insert_one.assert_called_once()
    assert _id == str(mock_inserted_id)


@patch("app.requests.post")
def test_retry_request_success_on_first_try(mock_post):
    """
    Test successful HTTP request on the first attempt.

    Args:
        mock_post: Mocked requests.post function

    Verifies:
        - Request succeeds on first try
        - Only one request attempt is made
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files)
    assert response == mock_response
    mock_post.assert_called_once()


@patch("app.requests.post")
def test_retry_request_success_after_retries(mock_post):
    """
    Test HTTP request succeeding after multiple retries.

    Args:
        mock_post: Mocked requests.post function

    Verifies:
        - Request succeeds after failed attempts
        - Correct number of retry attempts are made
    """
    mock_response = MagicMock()
    # Simulate failures then success
    mock_response.raise_for_status.side_effect = [
        requests.exceptions.HTTPError("Connection error"),
        requests.exceptions.HTTPError("Timeout"),
        None,  # Success on third attempt
    ]
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response == mock_response
    assert mock_post.call_count == 3
    assert mock_response.raise_for_status.call_count == 3


@patch("app.requests.post")
def test_retry_request_all_failures(mock_post):
    """
    Test HTTP request failing after all retry attempts.

    Args:
        mock_post: Mocked requests.post function

    Verifies:
        - Request fails after all retry attempts
        - Returns None after exhausting retries
        - Correct number of retry attempts are made
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Connection error"
    )
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response is None
    assert mock_post.call_count == 3
    assert mock_response.raise_for_status.call_count == 3


@patch("app.generate_stats_doc")
def test_home_route(mock_generate_stats_doc, test_client):
    """
    Test the home route (/) functionality.

    Args:
        mock_generate_stats_doc: Mocked function for generating stats document
        test_client: Flask test client fixture

    Verifies:
        - Route returns 200 status code
        - Cookie is set with database object ID
    """
    mock_id = str(ObjectId())
    mock_generate_stats_doc.return_value = mock_id
    response = test_client.get("/")
    assert response.status_code == 200
    assert "db_object_id" in response.headers["Set-Cookie"]


@patch("app.generate_stats_doc")
def test_home_route_with_existing_cookie(mock_generate_stats_doc, test_client):
    """
    Test home route behavior with pre-existing cookie.

    Args:
        mock_generate_stats_doc: Mocked function for generating stats document
        test_client: Flask test client fixture

    Verifies:
        - Route handles existing cookies correctly
        - Returns 200 status code
    """
    mock_id = str(ObjectId())
    mock_generate_stats_doc.return_value = mock_id
    test_client.set_cookie("db_object_id", mock_id)
    response = test_client.get("/")
    assert response.status_code == 200


@patch("app.generate_stats_doc")
def test_index_route(mock_generate_stats_doc, test_client):
    """
    Test the index route (/index) functionality.

    Args:
        mock_generate_stats_doc: Mocked function for generating stats document
        test_client: Flask test client fixture

    Verifies:
        - Route returns 200 status code
    """
    mock_id = str(ObjectId())
    mock_generate_stats_doc.return_value = mock_id
    response = test_client.get("/index")
    assert response.status_code == 200


@patch("app.collection")
@patch("app.generate_stats_doc")
def test_statistics_route(mock_generate_stats_doc, mock_collection, test_client):
    """
    Test the statistics route (/statistics) functionality.

    Args:
        mock_generate_stats_doc: Mocked function for generating stats document
        mock_collection: Mocked MongoDB collection
        test_client: Flask test client fixture

    Verifies:
        - Route returns 200 status code
        - Response contains expected statistics content
    """
    mock_id = str(ObjectId())
    mock_generate_stats_doc.return_value = mock_id
    test_client.set_cookie("db_object_id", mock_id)
    stats = {
        "Rock": {"wins": 1, "losses": 0, "ties": 0, "total": 1},
        "Paper": {"wins": 0, "losses": 1, "ties": 0, "total": 1},
        "Scissors": {"wins": 0, "losses": 0, "ties": 1, "total": 1},
        "Totals": {"wins": 1, "losses": 1, "ties": 1},
    }
    mock_collection.find_one.return_value = stats

    response = test_client.get("/statistics")
    assert response.status_code == 200
    assert b"Statistics" in response.data

@patch("app.retry_request")
def test_result_route_unknown_gesture(mock_retry_request, test_client):
    """
    Test result route handling of unknown gestures.

    Args:
        mock_retry_request: Mocked HTTP retry request function
        test_client: Flask test client fixture

    Verifies:
        - Route handles unknown gestures correctly
        - Returns 200 status code
        - Contains expected error message
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Unknown"}
    mock_retry_request.return_value = mock_response

    mock_id = str(ObjectId())
    test_client.set_cookie("db_object_id", mock_id)

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = test_client.post(
        "/result", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"Gesture not recognized" in response.data


@patch("app.retry_request")
def test_result_route_ml_failure(mock_retry_request, test_client):
    """
    Test result route handling of ML service failures.

    Args:
        mock_retry_request: Mocked HTTP retry request function
        test_client: Flask test client fixture

    Verifies:
        - Route handles ML service failures correctly
        - Returns 200 status code
        - Contains expected error message
    """
    mock_retry_request.return_value = None

    mock_id = str(ObjectId())
    test_client.set_cookie("db_object_id", mock_id)

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = test_client.post(
        "/result", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"No valid prediction" in response.data

@patch("app.retry_request")
def test_result_route_no_image(mock_retry_request, test_client):
    """
    Test result route handling when no image is provided.

    Args:
        mock_retry_request: Mocked HTTP retry request function
        test_client: Flask test client fixture

    Verifies:
        - Route handles missing image correctly
        - Returns 400 status code
        - Contains expected error message
    """
    mock_id = str(ObjectId())
    test_client.set_cookie("db_object_id", mock_id)
    
    response = test_client.post("/result", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"No image file provided" in response.data

@patch("app.collection.update_one")
@patch("app.retry_request")
def test_result_route_success(mock_retry_request, mock_update_one, test_client):
    """
    Test successful result route (/result) functionality.

    Args:
        mock_retry_request: Mocked HTTP retry request function
        mock_update_one: Mocked MongoDB update operation
        test_client: Flask test client fixture

    Verifies:
        - Route handles successful predictions correctly
        - Returns 200 status code
        - Contains expected success message
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Rock"}  # AI plays Rock
    mock_retry_request.return_value = mock_response

    mock_id = str(ObjectId())
    test_client.set_cookie("db_object_id", mock_id)

    # User plays Paper
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = test_client.post("/result", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert b"You win!" in response.data  # Paper beats Rock, so user wins
    