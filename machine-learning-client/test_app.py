"""
This module contains tests for the app's flower classification functionality.
It includes a test for predicting that a specific image belongs to the "Passion Fruit" class.
"""

from app import load_model, predict_plant

# Mock the flower name mapping
mock_flower_names = {
    "0": "Daffodil",
    "1": "Tiger Lily",
    "2": "Rose",
    "3": "Tulip",
    "4": "Sunflower",
    "5": "Passion Fruit",  # Assuming Passion Fruit is labeled as class 5
    # Add all other classes here...
}


def test_predict_passion_fruit():
    """
    Test that the image 'image_00001.jpg' is predicted as 'Passion Fruit'.
    This test ensures that the model correctly identifies the Passion Fruit image.
    """
    # Test image path
    test_image_path = "data/flowers-102/jpg/image_00001.jpg"

    # Use predict_plant to test
    model = load_model()
    predicted_plant = predict_plant(test_image_path, model, mock_flower_names)
    assert (
        predicted_plant == "Passion Fruit"
    ), f"Expected Passion Fruit but got {predicted_plant}"
