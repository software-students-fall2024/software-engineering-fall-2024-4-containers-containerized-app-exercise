"""
Unit tests for the plant prediction functionality in app.py.
"""

import sys
import pytest

#from ..app import main
#from machine_learning_client.app import main
from app import main
sys.path.insert(0, '../machine-learning-client')  # Ensure the correct path to app.py

# Mock the flower name mapping
mock_flower_names = {
    '0': 'Daffodil',
    '1': 'Tiger Lily',
    '2': 'Rose',
    '3': 'Tulip',
    '4': 'Sunflower',
    '5': 'Passion Fruit',  # Assuming Passion Fruit is labeled as class 5
}

@pytest.fixture
def test_predict_passion_fruit():
    """Tests that the image 'image_00001.jpg' is predicted as 'Passion Fruit'."""
    # Test image path
    test_image_path = 'data/flowers-102/jpg/image_00001.jpg'

    # Use the main function for testing
    predicted_plant = main(test_image_path)  # Ensure main returns a value

    # Assert that the predicted plant name is "Passion Fruit"
    assert predicted_plant == "Passion Fruit", f"Expected Passion Fruit but got {predicted_plant}"
