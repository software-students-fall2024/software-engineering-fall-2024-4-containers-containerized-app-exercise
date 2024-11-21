"""
Unit tests for the Flask application defined in `client.py`.
"""

# test_client.py
# cd machine-learning-client
# pytest test_client.py -v
# pytest -v

# pylint machine-learning-client/
# black .


from unittest.mock import patch, MagicMock
from io import BytesIO
import pytest
from client import app
from requests.exceptions import RequestException
from pymongo.errors import PyMongoError


@pytest.fixture(name="flask_client_fixture")
def create_flask_client():
    """
    Provide a Flask test client for testing application routes.

    Yields:
        FlaskClient: A test client for the Flask application.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Test successful prediction
@patch("client.rf_client")
@patch("client.collection")
def test_predict_success(
    mock_collection, mock_rf_client, flask_client_fixture
):  # pylint: disable=redefined-outer-name
    """
    Test that a successful image prediction returns the correct gesture and confidence,
    and that the prediction is stored in MongoDB.

    Args:
        mock_collection (MagicMock): Mock database collection to simulate `insert_one` behavior.
        mock_rf_client (MagicMock): Mock inference client to simulate `infer` behavior.
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Rock", "confidence": 0.95}]
    }

    # Mock the insert_one method
    mock_collection.insert_one.return_value = MagicMock()

    # Create a dummy image file
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}

    # Make a POST request to the /predict endpoint
    response = flask_client_fixture.post(
        "/predict", content_type="multipart/form-data", data=data
    )

    # Assert the response status and data
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Rock"
    assert json_data["confidence"] == 0.95

    # Ensure infer was called once
    mock_rf_client.infer.assert_called_once()

    # Ensure data was inserted into MongoDB once
    mock_collection.insert_one.assert_called_once()


# Test prediction with no image provided
def test_predict_no_image(flask_client_fixture):
    """
    Test that submitting a prediction request without an image returns a 400 error.

    Args:
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Make a POST request without image data
    response = flask_client_fixture.post(
        "/predict", content_type="multipart/form-data", data={}
    )

    # Assert the response status and error message
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No image file provided"


# Test inference API failure
@patch("client.rf_client")
def test_predict_inference_failure(
    mock_rf_client, flask_client_fixture
):  # pylint: disable=redefined-outer-name
    """
    Test that an inference API failure returns a 500 error with an appropriate message.

    Args:
        mock_rf_client (MagicMock): Mock inference client to simulate `infer` failure.
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Simulate an inference API failure with a caught exception
    mock_rf_client.infer.side_effect = RequestException("Inference API error")

    # Create a dummy image file
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}

    # Make a POST request to the /predict endpoint
    response = flask_client_fixture.post(
        "/predict", content_type="multipart/form-data", data=data
    )

    # Assert the response status and error message
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data["error"]


# Test MongoDB insertion failure
@patch("client.rf_client")
@patch("client.collection")
def test_predict_mongodb_failure(
    mock_collection, mock_rf_client, flask_client_fixture
):  # pylint: disable=redefined-outer-name
    """
    Test that a MongoDB insertion failure returns a 500 error with an appropriate message.

    Args:
        mock_collection (MagicMock): Mock database collection to simulate `insert_one` failure.
        mock_rf_client (MagicMock): Mock inference client to simulate successful `infer`.
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Paper", "confidence": 0.85}]
    }

    # Simulate a MongoDB insertion failure with a caught exception
    mock_collection.insert_one.side_effect = PyMongoError("MongoDB insertion error")

    # Create a dummy image file
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}

    # Make a POST request to the /predict endpoint
    response = flask_client_fixture.post(
        "/predict", content_type="multipart/form-data", data=data
    )

    # Assert the response status and error message
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data["error"]


# Test FileNotFoundError during file saving
@patch("client.rf_client")
@patch("os.makedirs")
def test_predict_file_not_found(
    mock_makedirs, mock_rf_client, flask_client_fixture
):  # pylint: disable=unused-argument, redefined-outer-name
    """
    Test that a FileNotFoundError during image file saving returns a 500 error.

    Args:
        mock_makedirs (MagicMock): Mock for `os.makedirs` to simulate directory creation.
        mock_rf_client (MagicMock): Mock inference client to simulate successful `infer`.
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Scissors", "confidence": 0.90}]
    }

    # Simulate a FileNotFoundError during file saving by patching the save method
    with patch(
        "werkzeug.datastructures.FileStorage.save",
        side_effect=FileNotFoundError("File not found"),
    ):
        # Create a dummy image file
        data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}

        # Make a POST request to the /predict endpoint
        response = flask_client_fixture.post(
            "/predict", content_type="multipart/form-data", data=data
        )

        # Assert the response status and error message
        assert response.status_code == 500
        json_data = response.get_json()
        assert "Prediction error" in json_data["error"]


# Test invalid inference response (missing 'class' key)
@patch("client.rf_client")
@patch("client.collection")
def test_predict_invalid_inference_response(
    mock_collection, mock_rf_client, flask_client_fixture
):  # pylint: disable=redefined-outer-name
    """
    Test that an invalid inference response (missing 'class' key) returns 'Unknown'
    gesture and 0 confidence.

    Args:
        mock_collection (MagicMock): Mock database collection to simulate `insert_one`.
        mock_rf_client (MagicMock): Mock inference client to simulate invalid `infer`
            response.
        flask_client_fixture (FlaskClient): Flask test client for making requests.
    """
    # Mock the inference result with missing 'class' key
    mock_rf_client.infer.return_value = {"predictions": [{"confidence": 0.80}]}

    # Create a dummy image file
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}

    # Make a POST request to the /predict endpoint
    response = flask_client_fixture.post(
        "/predict", content_type="multipart/form-data", data=data
    )

    # Assert the response status and default values
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Unknown"
    assert json_data["confidence"] == 0

    # Create expected data structure
    expected_data = {
        "gesture": "Unknown",
        "prediction_score": 0,
        "image_metadata": {"filename": "test_image.jpg"},
    }

    # Ensure data was inserted into MongoDB once with 'Unknown' gesture
    mock_collection.insert_one.assert_called_once_with(expected_data)
