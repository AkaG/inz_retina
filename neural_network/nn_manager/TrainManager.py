import os
from abc import abstractmethod
from typing import List

import h5py
from django.core.files import File
from django.core.files.base import ContentFile
from keras import callbacks

from neural_network.models import NeuralNetwork
from retina_scan import settings


class TrainManager(object):
    """
    Abstract class to train NN implement model and generators
    Set parameters
    """

    def __init__(self):
        self.model = self.create_model()
        self.nn = NeuralNetwork()
        self.nn.save()

        self.tmp_dir = os.path.join(settings.MEDIA_ROOT, "tmp")
        if not os.path.isdir(self.tmp_dir):
            os.makedirs(self.tmp_dir)

    def default_callbacks(self, directory) -> List:
        return [
            callbacks.ModelCheckpoint(os.path.join(directory, 'weights.{epoch:02d}-{val_loss:.2f}.hdf5'), monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1),
            callbacks.EarlyStopping(monitor='val_loss', min_delta=0.01, patience=5, verbose=0, mode='auto')
        ]

    def train_model(self, steps_per_epoch, validation_steps, epochs=5):
        # with tempfile.TemporaryDirectory(dir=settings.MEDIA_ROOT) as temp_dir:
        temp_dir = self.tmp_dir
        history = self.model.fit_generator(
            self.train_data_generator(),
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_data=self.test_data_generator(),
            validation_steps=validation_steps
            # callbacks=self.default_callbacks(temp_dir)
        )

        self.save_all(temp_dir)

    def save_all(self, directory):
        self.save_model(directory)
        self.save_best_weights(directory)
        self.nn.save()

    def save_model(self, directory):
        self.nn.model.save("nn_model", ContentFile(self.model.to_json()))

    def save_best_weights(self, directory):
        file_path = "nn_weights.h5"
        self.model.save_weights(file_path)
        with open(file_path, "rb") as weights:
            self.nn.weights = File(weights)

    @abstractmethod
    def create_model(self):
        pass

    @abstractmethod
    def train_data_generator(self):
        pass

    @abstractmethod
    def test_data_generator(self):
        pass
