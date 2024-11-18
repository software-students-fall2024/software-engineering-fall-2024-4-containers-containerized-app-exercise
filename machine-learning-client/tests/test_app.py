import pytest
import sys


from app import main, load_flower_names, load_model, predict_plant

# Mock the flower name mapping
mock_flower_names = {
    '0': 'Daffodil',
    '1': 'Tiger Lily',
    '2': 'Rose',
    '3': 'Tulip',
    '4': 'Sunflower',
    '5': 'Passion Fruit',  # Assuming Passion Fruit is labeled as class 5
    # Add all other classes here...
}

# Mocking the main prediction logic for testing
@pytest.fixture

# Test that the image 'image_00001.jpg' is predicted as 'Passion Fruit'
def test_predict_passion_fruit(setup):

    # Test image path
    test_image_path = 'data/flowers-102/jpg/image_00001.jpg'

    # Use the predict_plant function directly for testing
    predicted_plant = main(test_image_path)

    # Assert that the predicted plant name is "Passion Fruit"
    assert predicted_plant == "Passion Fruit", f"Expected Passion Fruit but got {predicted_plant}"
