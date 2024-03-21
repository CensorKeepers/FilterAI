from detoxify import Detoxify
from typing import List

model = None

def load_model_detoxify():
    global model
    model = Detoxify('multilingual')

def predict(sentences: List[str]) -> List[float]:
    predict = model.predict(sentences)
    return predict['toxicity']
