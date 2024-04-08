from detoxify import Detoxify
from typing import List

model = None


def load_model_detoxify():
    global model
    model = Detoxify('multilingual')


def predict(word: str) -> float:
    predict = model.predict(word)
    return predict['toxicity']
