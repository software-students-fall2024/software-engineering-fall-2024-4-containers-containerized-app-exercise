import pytest
import numpy as np
from unittest.mock import MagicMock
from ml_client import classify_image, preprocess_image, store_game_result


@pytest.fixture
def mock_model(mocker):
    """
    Fixture to mock the trained model's predict method.
    """
    mock_model = mocker.patch("ml_client.model")
    mock_model.predict.return_value = np.array([[0.1, 0.7, 0.2]])  # Mock prediction
    return mock_model


@pytest.fixture
def mock_games_collection():
    """
    Fixture to mock the MongoDB games collection.
    """
    mock_collection = MagicMock()
    return mock_collection


def test_preprocess_image():
    """
    Test that the image is resized and normalized correctly.
    """
    # Create a mock image tensor (300x300x3)
    mock_image = np.random.randint(0, 256, size=(300, 300, 3), dtype=np.uint8)
    preprocessed_image = preprocess_image(mock_image)

    # Check the shape
    assert preprocessed_image.shape == (224, 224, 3)

    # Check the pixel value range is [0, 1]
    assert np.all(preprocessed_image >= 0.0)
    assert np.all(preprocessed_image <= 1.0)


def test_classify_image(mock_model):
    """
    Test that classify_image returns the correct class based on the mocked model.
    """
    # Create a mock image array
    mock_image = np.random.rand(224, 224, 3)

    # Call classify_image
    result = classify_image(mock_image)

    # Assert the result matches the expected class
    assert result == "paper"  # Based on mock_model.predict output


def test_store_game_result(mock_games_collection):
    """
    Test that store_game_result inserts the correct game data into the database.
    """
    user_choice = "rock"
    computer_choice = "scissors"
    result = "win"

    # Call store_game_result
    game_data = store_game_result(
        mock_games_collection, user_choice, computer_choice, result
    )

    # Check that insert_one was called with the correct data
    mock_games_collection.insert_one.assert_called_once()
    inserted_data = mock_games_collection.insert_one.call_args[0][0]

    assert inserted_data["user_choice"] == user_choice
    assert inserted_data["computer_choice"] == computer_choice
    assert inserted_data["result"] == result
    assert "timestamp" in inserted_data  # Ensure timestamp is present
