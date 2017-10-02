import os

from data_module.models import ImageSeries, Image
from django.db.models import Max
from retina_scan import settings

import numpy as np
from skimage import data


class ImagePreprocessing():
    dir = os.path.join(settings.MEDIA_ROOT, "preprocessed")

    def __init__(self):
        self.create_dir()

        images = Image.objects.all()
        max_width, max_height = images.aggregate(Max('width_field'), Max('height_field'))

        print(max_width)
        print(max_height)

        for imageObject in images:
            image_path = os.path.join(settings.MEDIA_ROOT, imageObject.image.url)
            image = data.imread(image_path).astype(np.float64)

            self.preprocess_image(image)

    def create_dir(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

    def rgb2gray(self, image):
        return np.dot(image[..., :3], [0.299, 0.587, 0.114])

    def to_float(self, image):
        func = np.vectorize(lambda x: x / 255.0)

        return func(image)

    def normalize(self, image):
        min_val = np.amin(image)
        max_val = np.amax(image)

        image -= np.amin(image)
        image /= (max_val - min_val)

        return image

    def standardization(image):
        return (image - np.mean(image)) / np.std(image)

    def preprocess_image(self, image):
        # image = image[:, :, channel]
        # image = resize(image, (output_width, output_height))
        # image = to_float(image)
        # image = standardization(image)

        # Check if RGB image
        if len(image.shape) == 3:
            image = self.rgb2gray(image)

        image = self.standardization(image)