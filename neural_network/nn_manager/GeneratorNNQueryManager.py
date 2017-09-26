from abc import abstractmethod
from typing import List

import numpy as np
from keras.models import Model

from neural_network.nn_manager.NNQueryManager import NNQueryManager


class GeneratorNNQueryManager(NNQueryManager):
    @abstractmethod
    def create_model(self) -> Model:
        pass

    @abstractmethod
    def transform_image(self, image):
        pass

    def model_predict(self, image_gen, batch=4) -> List:
        ret = []
        for img in image_gen:
            imgs = self._get_batch(image_gen, batch=batch)
            pre = self.model.predict(np.array(imgs))
            ret.extend(pre)
        return ret

    def _get_batch(self, image_gen, batch):
        imgs = []
        for i in range(batch):
            try:
                imgs.append(self.transform_image(next(image_gen)))
            except StopIteration:
                return imgs
        return imgs
