import itertools

import numpy as np
import collections

import tensorflow as tf
from PIL import Image
from keras.models import Model, load_model
from keras import backend as K

from integrations.diagnosis_nn.diagnosisNN import DiagnosisNN
from neural_network.models import NeuralNetwork
from neural_network.nn_manager.GeneratorNNQueryManager import GeneratorNNQueryManager


class DiagnosisQuery(GeneratorNNQueryManager):
    input_shape = (100, 100, 1)
    db_description = 'diagnosis'

    def __init__(self):
        self.model = None
        self.sess = None

        super().__init__()

    def transform_image(self, image):
        if len(image.shape) == 2:
            image = image.reshape((image.shape[0], image.shape[1], 1))
        return image

    def create_model(self) -> Model:
        if self.model is None:
            try:
                nn = NeuralNetwork.objects.all().filter(description=self.db_description)
                if nn.count() > 0:
                    nn = nn.latest('created')

                self.sess = tf.Session()
                K.set_session(self.sess)
                self.model = load_model(nn.model.path)
                return self.model
            except IOError as e:
                print(e)

    def model_predict(self, image_gen, batch=3):
        if self.model is None:
            self._init_model()

        gen, gen_copy = itertools.tee(image_gen)

        with self.sess.as_default():
            result = super().model_predict(gen, batch=batch)

        return result
