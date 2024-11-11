""" Module to run the ml classification model """
import os
import torch

from torch import nn
from torch.nn import functional as F
from torchvision import transforms

# import the pre-trained model
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'mnist-cnn.pth')

class CNNModel(nn.Module):
    """ define cnn model class """
    def __init__(self):
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 3 * 3, 128)
        self.fc2 = nn.Linear(128, 10)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        """ ml forward function """
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 3 * 3)  # flatten
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = CNNModel()
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
model.eval()

class InvertGrayscale:
    def __call__(self, tensor):
        return 255.0 - tensor


test_transform = transforms.Compose([
    transforms.ToTensor(),
    # inverted here due to nature of how data is outputted from webpage
    InvertGrayscale(),
    transforms.Resize((28, 28)),
    transforms.Normalize((254.8692,), (0.3015,))
])

def mnist_classify(data):
    """ receives web-app data and returns the model output """
    model_input = test_transform(data).unsqueeze(0)
    with torch.no_grad():
        output = model(model_input)
        prediction = output.argmax(dim=1, keepdim=True).item()
    return prediction
