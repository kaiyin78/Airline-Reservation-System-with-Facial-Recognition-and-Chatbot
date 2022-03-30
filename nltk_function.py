import nltk
#nltk.download('punkt')
import numpy as np
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()


def tokenize(sentence):
    return nltk.word_tokenize(sentence)


def stem(word):
    return stemmer.stem(word.lower())


def words(tokenized_sentence, all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]
    bags = np.zeros(len(all_words), dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bags[idx] = 1

    return bags


sentence = ["hello", "how", "bye", "You"]
word = ["hi", "hello", "I", "you", "bye", "how", "cool"]

bog = words(sentence, word)
print(bog)
