import os
import tempfile

from django.core.files.base import ContentFile, File

from neural_network.models import NeuralNetwork
from neural_network.nn_manager.AbstractNNSave import AbstractNNSave
from retina_scan import settings


class DBNNSave(AbstractNNSave):
    def __init__(self):
        self.nn = NeuralNetwork()

    def save_model(self, model):
        self.nn.model.save("nn_model", ContentFile(model.to_json()))

    def save_weights(self, model):
        with tempfile.TemporaryDirectory(dir=settings.MEDIA_ROOT) as temp_dir:
            file_path = os.path.join(temp_dir, "nn_weights.h5")
            model.save_weights(file_path)
            with open(file_path, "rb") as weights:
                self.nn.weights.save("nn_weights.h5", File(weights))

