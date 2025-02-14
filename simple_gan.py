# -*- coding: utf-8 -*-
"""Simple GAN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qmR4Sc1INdK6bekrYU9VyuhZwm08UNlp
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from torchvision.utils import save_image
import os

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Hyperparameters
latent_size = 64
hidden_size = 256
image_size = 784  # 28*28
num_epochs = 10
batch_size = 100
learning_rate = 0.0002

# Transform for MNIST data
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.5,), std=(0.5,))
])

# MNIST dataset
mnist = torchvision.datasets.MNIST(root='./data', train=True, transform=transform, download=True)
data_loader = DataLoader(dataset=mnist, batch_size=batch_size, shuffle=True)

# Discriminator
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(image_size, hidden_size),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

# Generator
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, image_size),
            nn.Tanh()
        )

    def forward(self, x):
        return self.model(x)

# Initialize models
D = Discriminator().to(device)
G = Generator().to(device)

# Loss and optimizers
criterion = nn.BCELoss()
d_optimizer = optim.Adam(D.parameters(), lr=learning_rate)
g_optimizer = optim.Adam(G.parameters(), lr=learning_rate)

# Function to create real and fake labels
def real_labels(size):
    data = torch.ones(size, 1).to(device)
    return data

def fake_labels(size):
    data = torch.zeros(size, 1).to(device)
    return data

# Function to create noise
def noise(size):
    n = torch.randn(size, latent_size).to(device)
    return n

# Function to save fake images
def save_fake_images(index, fake_images):
    fake_images = fake_images.reshape(fake_images.size(0), 1, 28, 28)
    fake_fname = f'./output/fake_images-{index:04d}.png'
    save_image(fake_images, fake_fname)
    print(f'Saving {fake_fname}')

# Create output directory
os.makedirs('./output', exist_ok=True)

# Training loop
for epoch in range(num_epochs):
    for i, (images, _) in enumerate(data_loader):
        batch_size = images.size(0)
        images = images.reshape(batch_size, -1).to(device)

        # Train Discriminator
        d_optimizer.zero_grad()

        outputs = D(images)
        d_loss_real = criterion(outputs, real_labels(batch_size))
        real_score = outputs

        z = noise(batch_size)
        fake_images = G(z)
        outputs = D(fake_images)
        d_loss_fake = criterion(outputs, fake_labels(batch_size))
        fake_score = outputs

        d_loss = d_loss_real + d_loss_fake
        d_loss.backward()
        d_optimizer.step()

        # Train Generator
        g_optimizer.zero_grad()

        z = noise(batch_size)
        fake_images = G(z)
        outputs = D(fake_images)

        g_loss = criterion(outputs, real_labels(batch_size))

        g_loss.backward()
        g_optimizer.step()

        if (i+1) % 200 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(data_loader)}], d_loss: {d_loss.item():.4f}, g_loss: {g_loss.item():.4f}, D(x): {real_score.mean().item():.2f}, D(G(z)): {fake_score.mean().item():.2f}')

    # Save generated images at each epoch
    save_fake_images(epoch + 1, fake_images)

print("Training finished!")

# Visualize some generated images
z = noise(batch_size)
fake_images = G(z)
fake_images = fake_images.reshape(fake_images.size(0), 1, 28, 28)
fake_images = fake_images.data.cpu()

grid = torchvision.utils.make_grid(fake_images, nrow=10, normalize=True)
plt.imshow(grid.permute(1, 2, 0))
plt.show()

