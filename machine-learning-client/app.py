"""
This module performs flower classification using a pre-trained ResNet50 model.
It includes functions to load the flower class names, initialize the model, 
transform images, and predict the flower name based on an input image.
"""

import os
import json
import torch
from torchvision import transforms
from PIL import Image
import torchvision
from flask import Flask, jsonify, request, send_from_directory
from pymongo import MongoClient
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "plant_identifier")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]

# Initialize Flask app
app = Flask(__name__)


def load_flower_names():
    """
    Load flower class names from the flower_to_name.json file.

    Returns:
        dict: A dictionary mapping flower class indices to names.
    """
    with open("data/flower_to_name.json", encoding="utf-8") as file:
        return json.load(file)


def load_model():
    """
    Load and initialize the ResNet50 model for flower classification.

    Returns:
        torch.nn.Module: A ResNet50 model with the last layer modified for 102 classes.
    """
    # Initialize the model architecture with ResNet50
    model = torchvision.models.resnet50(
        weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V2
    )

    # Modify the last fully connected layer to match the number of classes
    num_classes = 102
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

    # Load the saved model's state_dict into the modified model
    model.load_state_dict(
        torch.load(
            "flower_classification_resnet.pth",
            map_location=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        )
    )

    # Set the model to evaluation mode
    model.eval()

    # Move the model to the appropriate device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    return model


def transform_image(image_path):
    """
    Apply image transformations to prepare the input image for the model.

    Args:
        image_path (str): Path to the image file.

    Returns:
        torch.Tensor: Transformed image tensor with added batch dimension.
    """
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image_path).convert("RGB")  # Convert image to RGB
    return transform(image).unsqueeze(0)  # Add batch dimension


def predict_plant(image_path):
    """
    Predict the plant name from an input image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Predicted plant name.
    """
    # Preprocess the image
    image_tensor = transform_image(image_path)

    # Move the image to the same device as the model (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    image_tensor = image_tensor.to(device)

    # Get the model's predictions
    with torch.no_grad():
        outputs = TRAINED_MODEL(image_tensor)
        _, predicted_class = torch.max(outputs, 1)
        predicted_class_id = predicted_class.item() + 1  # Adjust for zero-based index

    # Map the predicted class ID to the plant name
    plant_name = FLOWER_CLASS_NAMES.get(str(predicted_class_id), "Unknown plant")
    return plant_name


# Load the model and flower names once when the app starts
FLOWER_CLASS_NAMES = load_flower_names()
TRAINED_MODEL = load_model()


@app.route("/predict", methods=["POST"])
def predict():
    """
    Predicts the plant name from an uploaded image file.

    Returns:
        Response: JSON response containing the predicted plant name.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]

    # Save the image to a temporary location
    image_path = os.path.join("/tmp", secure_filename(image_file.filename))
    image_file.save(image_path)

    try:
        # Predict the plant name
        plant_name = predict_plant(image_path)
    finally:
        # Clean up the temporary file
        if os.path.exists(image_path):
            os.remove(image_path)

    return jsonify({"plant_name": plant_name}), 200


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Serve uploaded files.

    Args:
        filename (str): Name of the file to serve.

    Returns:
        Response: The requested file.
    """
    uploads_dir = os.path.join(app.root_path, "static", "uploads")
    return send_from_directory(uploads_dir, filename)


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "3001")
    CORS(app)
    app.run(host="0.0.0.0", port=FLASK_PORT)
    