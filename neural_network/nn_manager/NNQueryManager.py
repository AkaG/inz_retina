from abc import abstractmethod
from typing import List

from keras.models import Model


class NNQueryManager(object):
    def __init__(self, model=None):
        self._init_model(model)

    def _init_model(self, model=None):
        if model is None:
            self.model = self.create_model()
        else:
            self.model = model

    @abstractmethod
    def create_model(self) -> Model:
        pass

    @abstractmethod
    def model_predict(self, image_gen) -> List:
        pass
