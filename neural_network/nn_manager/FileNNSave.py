import os

from neural_network.nn_manager.AbstractNNSave import AbstractNNSave


class FileNNSave(AbstractNNSave):
    def __init__(self, path):
        self.path = path

    def save_model(self, model):
        with open(os.path.join(self.path, 'nn_model.js'), "w") as file:
            file.write(model.to_json())

    def save_weights(self, model):
        model.save_weights(os.path.join(self.path, 'nn_weights.h5'))