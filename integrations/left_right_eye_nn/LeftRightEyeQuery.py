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


class LeftRightEyeQuerySingleton(object):
    query = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.query is None:
            cls.query = LeftRightEyeQuery()
        return cls.query
