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

    def model_predict(self, image_gen, batch=5) -> List:
        ret = {}
        while True:
            names, imgs = self._get_batch(image_gen, batch=batch)
            if len(names) == 0:
                break

            pre = self.model.predict(np.array(imgs))
            for name, pred in zip(names, pre):
                ret[name] = pred
        return ret

    def _get_batch(self, image_gen, batch):
        names = []
        imgs = []
        for i in range(batch):
            try:
                name, img = next(image_gen)
                names.append(name)
                imgs.append(self.transform_image(img))
            except StopIteration:
                return names, imgs
        return names, imgs
