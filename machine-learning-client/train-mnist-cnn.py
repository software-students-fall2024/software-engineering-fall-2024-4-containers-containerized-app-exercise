import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms


class CNNModel(nn.Module):
    def __init__(self):
        super(CNNModel, self).__init__()
        # 1 input channel (grayscale), 32 output channels
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 3 * 3, 128)
        self.fc2 = nn.Linear(128, 10)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 3 * 3)  # flatten
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


model = CNNModel()

# ensure that images have black digits with white background


class InvertGrayscale:
    def __call__(self, tensor):
        return 255.0 - tensor


transform = transforms.Compose([
    transforms.ToTensor(),
    InvertGrayscale()
])

dataset = datasets.MNIST(root='./data', train=True,
                         download=True, transform=transform)
loader = torch.utils.data.DataLoader(
    dataset, batch_size=64, shuffle=False, num_workers=0)

mean = 0.0
std = 0.0
total_images = 0

for images, _ in loader:
    batch_samples = images.size(0)  # batch size
    # flatten the spatial dimensions
    images = images.view(batch_samples, images.size(1), -1)
    mean += images.mean(2).sum(0)
    std += images.std(2).sum(0)
    total_images += batch_samples

mean /= total_images
std /= total_images

charCount = 100

print("\n" + "=" * charCount + "\n")
print("DEBUG: Dataset Characteristics")
print(f" * Mean: {float(mean):.4f}")
print(f" * Std: {float(std):.4f}")
print("\n" + "=" * charCount + "\n")

train_transform = transforms.Compose([
    transforms.RandomRotation(degrees=10),    # randomly rotate images
    transforms.RandomAffine(degrees=0, translate=(
        0.1, 0.1)),  # randomly translate images
    transforms.RandomResizedCrop(28, scale=(
        0.9, 1.1)),  # randomly scale images
    transforms.ToTensor(),
    InvertGrayscale(),
    transforms.Normalize((mean,), (std,))
])

test_transform = transforms.Compose([
    transforms.ToTensor(),
    InvertGrayscale(),
    transforms.Normalize((mean,), (std,))
])

train_dataset = datasets.MNIST(
    root='./data', train=True, download=True, transform=train_transform)
test_dataset = datasets.MNIST(
    root='./data', train=False, download=True, transform=test_transform)

train_loader = torch.utils.data.DataLoader(
    train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(
    test_dataset, batch_size=1000, shuffle=False)


def train(model, train_loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)

        # zero gradients
        optimizer.zero_grad()

        # forward pass
        output = model(data)

        # compute loss
        loss = criterion(output, target)

        # backward pass & optimization
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)
    print(f'Train Loss: {avg_loss:.4f}')
    return avg_loss


def test(model, test_loader, criterion, device):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)

            # forward pass
            output = model(data)

            # compute loss
            test_loss += criterion(output, target).item()

            # get predictions
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader)
    accuracy = 100. * correct / len(test_loader.dataset)
    print(f'Test Loss: {test_loss:.4f}, Accuracy: {accuracy:.2f}%')
    return test_loss, accuracy


# device specifications
device = torch.device("mps" if torch.mps.is_available() else "cpu")

# hyperparameters
epochs = 10
learning_rate = 0.001

# init model, criterion, and optimizer
model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

print("DEBUG: \x1B[4mModel Training and Evaluation\x1B[0m" + "\n")
# train test loop
for epoch in range(1, epochs + 1):
    print(f'Epoch {epoch}/{epochs}')
    train_loss = train(model, train_loader, optimizer, criterion, device)
    test_loss, accuracy = test(model, test_loader, criterion, device)
print("\n" + "=" * charCount + "\n")

# save model
torch.save(model.state_dict(), 'mnist-cnn.pth')
print("DEBUG: \x1B[1mModel Saved!\x1B[0m")
print("\n" + "=" * charCount)
