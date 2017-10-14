import os

import PIL
import numpy as np

from PIL import Image

from neural_network.nn_manager.AbstractDataGenerator import AbstractDataGenerator


class DataGenerator(AbstractDataGenerator):
    def __init__(self, img_shape):
        self.input_shape = img_shape

    def flow_from_directory(self, path):
        for fname in os.listdir(path):
            if fname.endswith('.jpg'):
                yield fname, self.preprocess_image(Image.open(os.path.join(path, fname)))

    def flow(self, files, names):
        for file, name in zip(files, names):
            yield name, self.preprocess_image(file)

    def preprocess_image(self, image):
        if type(image) is not PIL.JpegImagePlugin.JpegImageFile:
            image = Image.fromarray(image)
        image = image.convert('L').resize((self.input_shape[0], self.input_shape[1]))
        image = self._normalize(np.asarray(image, dtype=np.float32))
        return image

    def _normalize(self, image):
        img = np.copy(image)
        min = np.amin(img)
        max = np.amax(img)
        img -= min
        img /= max - min
        return img
