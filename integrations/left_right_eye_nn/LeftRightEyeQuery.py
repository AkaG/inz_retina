import numpy as np
from keras.models import Model

from integrations.left_right_eye_nn.LeftRightEyeNN import LeftRightEyeNN
from neural_network.nn_manager.GeneratorNNQueryManager import GeneratorNNQueryManager


class LeftRightEyeQuery(GeneratorNNQueryManager):
    def __init__(self):
        self.nn = LeftRightEyeNN()
        super().__init__()

    def transform_image(self, image):
        ret = image.resize((self.nn.input_shape[0], self.nn.input_shape[1]))
        norm = self._normalize(np.asarray(ret))
        if len(norm.shape) is 2:
            return np.array([[[x, x, x] for x in y] for y in norm])
        else:
            return np.array(norm)

    def _normalize(self, img):
        arr = img.astype('float32')

        # minval = np.amin(arr)
        # maxval = np.amax(arr)
        # arr -= minval
        # arr /= (maxval - minval)

        return arr * (1. / 255)

    def create_model(self) -> Model:
        nn = LeftRightEyeNN()
        return nn.model


class LeftRightEyeQuerySingleton(object):
    query = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.query is None:
            cls.query = LeftRightEyeQuery()
        return cls.query
