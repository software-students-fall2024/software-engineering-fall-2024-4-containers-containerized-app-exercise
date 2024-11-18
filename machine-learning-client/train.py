import os
import scipy.io
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from tqdm import tqdm
from sklearn.metrics import accuracy_score



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load labels from .mat file
def load_labels(mat_file):
    data = scipy.io.loadmat(mat_file)
    print(data)
    return data['labels'].squeeze() - 1  # Adjust to zero-based indexing if needed


# Custom dataset class
class FlowerDataset(Dataset):
    def __init__(self, img_dir, labels, transform=None):
        self.img_dir = img_dir
        self.labels = labels
        self.transform = transform
        self.image_files = sorted([f for f in os.listdir(img_dir) if f.endswith('.jpg')])

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.image_files[idx])
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

def main():
    # Set paths
    img_dir = 'data/flowers-102/jpg'         # Change to your image directory
    label_file = 'data/flowers-102/imagelabels.mat'  # Change to your .mat file path

    # Load labels
    labels = load_labels(label_file)


    # Define data transformations
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # Create dataset and dataloaders
    dataset = FlowerDataset(img_dir, labels, transform=transform)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4 if torch.cuda.is_available() else 0, pin_memory=True)

    # Load pre-trained ResNet model and modify the classifier
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)  # Use up-to-date weights
    num_classes = len(np.unique(labels))

    # Freeze all layers except the last fully connected layer
    for param in model.parameters():
        param.requires_grad = False

    # Replace the last layer with a new layer matching the number of classes
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model = model.to(device)

    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=1e-4)

    # Initialize mixed-precision scaler if using CUDA
    use_amp = torch.cuda.is_available()
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    # Training loop
    epochs = 1
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}, starting training phase")
        model.train()
        running_loss = 0.0

        # Wrap the training loop with tqdm to show a progress bar
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}", unit="batch"):
            images, labels = images.to(device), labels.to(device)

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward pass with or without mixed precision
            if use_amp:
                with torch.cuda.amp.autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

            running_loss += loss.item() * images.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")
        # Print the accuracy of the model
        print(f"Accuracy: {accuracy_score(labels, outputs.argmax(dim=1))}")

    # Save the trained model parameters
    save_path = 'flower_classification_resnet.pth'
    torch.save(model.state_dict(), save_path)
    print(f"Model parameters saved to {save_path}")

if __name__ == '__main__':
    main()
