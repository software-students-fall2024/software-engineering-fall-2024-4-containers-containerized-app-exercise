import pytest
import json
import numpy as np
from io import BytesIO
from PIL import Image
from ml_client import app, preprocess_image


@pytest.fixture
def client():
    """
    Fixture to set up the Flask test client.
    """
    with app.test_client() as client:
        yield client


def create_image_array():
    """
    Helper function to create a dummy image array for testing.
    """
    image = Image.new("RGB", (224, 224), color=(255, 0, 0))  # Create a red image
    image_array = np.array(image) / 255.0  # Normalize
    return image_array


def test_classify_success(client):
    """
    Test the /classify endpoint with a valid image array.
    """
    image_array = create_image_array().tolist()

    # Debugging: Print the payload being sent
    print(f"Payload being sent: {type(image_array)}, Length: {len(image_array)}")

    response = client.post(
        "/classify",
        data=json.dumps({"image_array": image_array}),
        content_type="application/json",
        timeout=10,
    )
    assert response.status_code == 200
    assert "result" in response.json


def test_classify_missing_image_array(client):
    """
    Test the /classify endpoint with a missing image array.
    """
    response = client.post(
        "/classify", data=json.dumps({}), content_type="application/json", timeout=10
    )
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "No image_array provided"


def test_store_success(client):
    """
    Test the /store endpoint with valid game results.
    """
    payload = {
        "user_choice": "rock",
        "computer_choice": "scissors",
        "result": "win",
    }
    response = client.post(
        "/store", data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 200
    assert "status" in response.json
    assert response.json["status"] == "success"


def test_store_missing_fields(client):
    """
    Test the /store endpoint with missing fields.
    """
    payload = {
        "user_choice": "rock",
        "computer_choice": "scissors",
    }  # Missing "result"
    response = client.post(
        "/store", data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Missing required fields"


def test_preprocess_image():
    """
    Test the preprocess_image function to ensure resizing and normalization.
    """
    image_array = create_image_array()
    processed_image = preprocess_image(image_array).numpy()  # Convert to NumPy array
    assert processed_image.shape == (
        300,
        300,
        3,
    )  # Updated to match the model's input shape
    assert (processed_image >= 0).all() and (processed_image <= 1).all()
