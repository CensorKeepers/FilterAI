from detoxify import Detoxify

model = None

def load_model_detoxify():
    global model
    model =  Detoxify('multilingual')

def predict_detoxify(sentences):
    predict = model.predict(sentences)
    return predict
