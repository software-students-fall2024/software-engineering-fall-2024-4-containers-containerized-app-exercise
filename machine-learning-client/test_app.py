"""
Unit tests for the app.py module, which performs flower classification using a ResNet50 model.
This script tests each function independently to achieve a minimum of 80% code coverage.
"""

import unittest.mock
import pytest
import torch
from unittest.mock import patch, MagicMock
from PIL import Image
from app import load_flower_names, load_model, transform_image, predict_plant


def test_load_flower_names():
    """Test loading flower names from a JSON file."""
    with patch("builtins.open", unittest.mock.mock_open(read_data='{"1": "Rose", "2": "Tulip"}')):
        flower_names = load_flower_names()
        assert flower_names == {"1": "Rose", "2": "Tulip"}


def test_load_model():
    """Test loading and initializing the ResNet50 model."""
    with patch("torchvision.models.resnet50") as mock_resnet50:
        model_instance = MagicMock()
        mock_resnet50.return_value = model_instance
        model = load_model()
        assert model is not None
        mock_resnet50.assert_called_once()


def test_transform_image():
    """Test transforming an image to a tensor for model input."""
    # Create an in-memory image
    img = Image.new("RGB", (224, 224), color="red")
    with patch("PIL.Image.open", return_value=img):
        tensor = transform_image("path/to/image.jpg")
        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (1, 3, 224, 224)  # Expecting a (1, 3, 224, 224) size tensor with batch dim.


def test_predict_plant():
    """Test predicting the plant name using the model and flower names dictionary."""
    flower_names = {"1": "Rose", "2": "Tulip"}
    model = MagicMock()
    model.return_value = torch.tensor([[0.1, 0.9]])  # Mock prediction output

    with patch("app.transform_image") as mock_transform:
        mock_transform.return_value = torch.tensor([[[[0.1]]]])  # Mocked tensor input
        result = predict_plant("path/to/image.jpg", model, flower_names)
        assert result == "Tulip"  # Highest probability for class "2" which is "Tulip"

