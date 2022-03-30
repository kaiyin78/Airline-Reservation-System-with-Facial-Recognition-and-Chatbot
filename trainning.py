import numpy as np
import random
import json

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from nltk_function import words, tokenize, stem
from Model import NeuralNet

with open('intent.json', 'r') as f:
    intents = json.load(f)

All_words = []
Tags = []
xy = []

for intent in intents['intents']:
    Tag = intent['tag']
    #  tag list
    Tags.append(Tag)
    for pattern in intent['patterns']:
        # tokenize each word in the sentence
        w = tokenize(pattern)
        # words list
        All_words.extend(w)
        # add to xy
        xy.append((w, Tag))

# stem and lower each word
ignore = ['?', '.', '!']
All_words = [stem(w) for w in All_words if w not in ignore]
# remove duplicates and sort
All_words = sorted(set(All_words))
tags = sorted(set(Tags))

print(len(xy), "patterns")
print(len(Tags), "tags:", Tags)
print(len(All_words), "unique stemmed words:", All_words)

# training data
X = []
y = []
for (pattern_sentence, tag) in xy:
    # X: bag of words for each pattern_sentence
    bag = words(pattern_sentence, All_words)
    X.append(bag)
    # y: PyTorch CrossEntropyLoss needs only class labels, not one-hot
    label = tags.index(tag)
    y.append(label)

X = np.array(X)
y = np.array(y)

# Hyper-parameters
num_epochs = 1000
batch_size = 8
learning = 0.001
input_size = len(X[0])
hidden_size = 8
output_size = len(Tags)
print(input_size, output_size)


class ChatDataset(Dataset):

    def __init__(self):
        self.n_samples = len(X)
        self.x_data = X
        self.y_data = y

    # support indexing such that dataset[i] can be used to get i-th sample
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    # we can call len(dataset) to return the size
    def __len__(self):
        return self.n_samples


dataset = ChatDataset()
loader = DataLoader(dataset=dataset,
                    batch_size=batch_size,
                    shuffle=True,
                    num_workers=0)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = NeuralNet(input_size, hidden_size, output_size).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning)

# Train the model
for epoch in range(num_epochs):
    for (words, labels) in loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        # Forward pass
        outputs = model(words)
        # if y would be one-hot, we must apply
        # labels = torch.max(labels, 1)[1]
        loss = criterion(outputs, labels)

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

print(f'final loss: {loss.item():.4f}')

data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": All_words,
    "tags": tags
}

file = "data.pth"
torch.save(data, file)

print(f'training complete. file saved to {file}')
