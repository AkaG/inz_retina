import os

from neural_network.store.AbstractNNSave import AbstractNNSave


class FileNNSave(AbstractNNSave):
    def __init__(self, path, model_file_name='nn_model.h5', weights_file_name='nn_weights.h5'):
        self.path = path
        self.model_file_name = model_file_name
        self.weights_file_name = weights_file_name

    def save_model(self, model):
        model.save(os.path.join(self.path, self.model_file_name))

    def save_weights(self, model):
        model.save_weights(os.path.join(self.path, self.weights_file_name))