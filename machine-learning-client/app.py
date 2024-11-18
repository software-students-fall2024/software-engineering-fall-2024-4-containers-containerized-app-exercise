import torch
from torchvision import transforms
from PIL import Image
import json
import torchvision

# Load the flower class names from the flower_to_name.json file
def load_flower_names():
    with open('data/flower_to_name.json') as f:
        return json.load(f)

def load_model():
    # Initialize the model architecture with ResNet50
    model = torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V2)
    
    # Modify the last fully connected layer to match the number of classes (102 for the flower dataset)
    num_classes = 102
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    
    # Load the saved model's state_dict into the modified model
    model.load_state_dict(torch.load('flower_classification_resnet.pth', map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu')))
    
    # Set the model to evaluation mode
    model.eval()
    
    # Move the model to the appropriate device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    return model


# Define the image transformation
def transform_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(image_path)
    return transform(image).unsqueeze(0)  # Add batch dimension

# Predict the plant name
def predict_plant(image_path, model, flower_names):
    # Preprocess the image
    image_tensor = transform_image(image_path)
    
    # Move the image to the same device as the model (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    image_tensor = image_tensor.to(device)
    
    # Get the model's predictions
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted_class = torch.max(outputs, 1)
        predicted_class_id = predicted_class.item() + 1
    
    # Map the predicted class ID to the plant name
    plant_name = flower_names.get(str(predicted_class_id), "Unknown plant")
    return plant_name

# Example usage
def main(image_path):
    flower_names = load_flower_names()  # Load flower name mapping
    model = load_model()  # Load the pre-trained model
    plant_name = predict_plant(image_path, model, flower_names)
    print(f"Predicted plant: {plant_name}")

main('data/flowers-102/jpg/image_00001.jpg')
