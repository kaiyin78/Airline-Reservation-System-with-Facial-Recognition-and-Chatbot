import random
import json

import torch

from Model import NeuralNet
from nltk_function import words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intent.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()
print(tags)


def make_responese(sentence):
    sentence = tokenize(sentence)
    X = words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.70:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                result = random.choice(intent['responses'])
                if tag == "seat":
                    result = "seat"
                if tag == "order":
                    result = "order"
                if tag == "admin":
                    result = "admin"
    else:
        result = "I dont understand!!!"

    return result
