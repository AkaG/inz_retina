import itertools

import numpy as np
from PIL import Image
from keras.models import Model

from integrations.left_right_eye_nn.LeftRightEyeNN import LeftRightEyeNN
from neural_network.nn_manager.GeneratorNNQueryManager import GeneratorNNQueryManager


class LeftRightEyeQuery(GeneratorNNQueryManager):
    def __init__(self):
        self.nn = LeftRightEyeNN()
        super().__init__()

    def transform_image(self, image):
        if len(image.shape) == 2:
            image = image.reshape((image.shape[0], image.shape[1], 1))
        return image

    def create_model(self) -> Model:
        nn = LeftRightEyeNN()
        return nn.model

    def model_predict(self, image_gen, batch=5):
        gen, gen_copy = itertools.tee(image_gen)
        org = super().model_predict(gen, batch=batch)
        flipped = super().model_predict(self._override_generator(gen_copy), batch=batch)
        return self._to_category(self._combine_results(org, flipped))

    def _to_category(self, result_dict):
        for x in result_dict:
            if result_dict[x] < 0.45:
                result_dict[x] = 'L'
            elif result_dict[x] > 0.55:
                result_dict[x] = 'R'
            else:
                result_dict[x] = 'N'

        return result_dict

    def _combine_results(self, org, flipped):
        to_return = {}
        for name in org:
            result = org[name]
            flipped_result = flipped[name]
            to_return[name] = np.mean([result, 1 - flipped_result])
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
        if cls.query is None:
            cls.query = LeftRightEyeQuery()
        return cls.query
