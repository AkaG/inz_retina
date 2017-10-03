import os

import numpy as np
from PIL.Image import Image

from neural_network.nn_manager.AbstractDataGenerator import AbstractDataGenerator


class DataGenerator(AbstractDataGenerator):
    def flow_from_directory(self, path):
        for name in os.listdir(path):
            if name.endswith('.jpg'):
                yield name, np.asarray(Image.open(os.path.join(path, name)))

    def flow(self, files, names):
        for file, name in zip(files, names):
            yield name, file
