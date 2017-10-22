import json

from keras.models import model_from_json


def load_model_from_json_file(file_path):
    with open(file_path) as file:
        return model_from_json(json.dumps(json.load(file.read())))


def load_weights_from_file(model, file_path):
    model.load_weights(file_path)
    return model
