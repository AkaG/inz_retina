import itertools

import numpy as np
import tensorflow as tf
from PIL import Image
from keras.models import Model, load_model

from integrations.left_right_eye_nn.LeftRightEyeNN import LeftRightEyeNN
from neural_network.models import NeuralNetwork
from neural_network.nn_manager.GeneratorNNQueryManager import GeneratorNNQueryManager

lr_nn_model = None
lr_graph = None


class LeftRightEyeQuery(GeneratorNNQueryManager):
    input_shape = LeftRightEyeNN.input_shape
    db_description = LeftRightEyeNN.db_description

    def __init__(self):
        super().__init__()

    def transform_image(self, image):
        if len(image.shape) == 2:
            image = image.reshape((image.shape[0], image.shape[1], 1))
        return image

    def create_model(self) -> Model:
        global lr_nn_model
        global lr_graph
        if lr_nn_model is None:
            try:
                nn = NeuralNetwork.objects.all().filter(description=self.db_description)
                if nn.count() > 0:
                    nn = nn.latest('created')
                lr_nn_model = load_model(nn.model.path)
                lr_graph = tf.get_default_graph()
            except IOError:
                lr_nn_model = None
                lr_graph = None
                raise IOError
        return lr_nn_model

    def model_predict(self, image_gen, batch=5):
        if self.model is None:
            self._init_model()

        gen, gen_copy = itertools.tee(image_gen)
        global lr_graph
        with lr_graph.as_default():
            org = super().model_predict(gen, batch=batch)
            flipped = super().model_predict(self._override_generator(gen_copy), batch=batch)
        return self._predict_category(self._combine_results(org, flipped))

    def _predict_category(self, result_dict):
        for x in result_dict:
            res = {}
            res['value'] = result_dict[x]
            res['prediction'] = self._to_category(result_dict[x])
            result_dict[x] = res
        return result_dict

    def _to_category(self, value):
        if value < 0.45:
            return 'L'
        elif value > 0.55:
            return 'R'
        else:
            return 'N'

    def _combine_results(self, org, flipped):
        to_return = {}
        for name in org:
            result = org[name]
            flipped_result = flipped[name]
            to_return[name] = float('{0:.3f}'.format(np.mean([result, 1 - flipped_result])))
        return to_return

    def _override_generator(self, gen):
        try:
            while True:
                name, img = next(gen)
                img = Image.fromarray(img)
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                yield name, np.asarray(img)
        except StopIteration:
            raise StopIteration()


class LeftRightEyeQuerySingleton(object):
    query = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        # backend.clear_session()
        if cls.query is None:
            cls.query = LeftRightEyeQuery()
        return cls.query
