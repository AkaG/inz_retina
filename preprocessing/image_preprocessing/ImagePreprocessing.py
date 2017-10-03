import os

from pylab import *
from data_module.models import Image
from django.db.models import Max
from retina_scan import settings

import numpy as np
from skimage import data
from skimage.transform import resize


class ImagePreprocessing():
    dir = os.path.join(settings.MEDIA_ROOT, "preprocessed")

    def __init__(self, width, height):
        self.create_dir()

        images = Image.objects.all()

        query = images.aggregate(max_width=Max('width_field'), max_height=Max('height_field'))
        max_width = query['max_width']
        max_height = query['max_height']

        if width and height:
            max_width = width
            max_height = height

        for imageObject in images:
            new_image_path = os.path.join(self.dir, imageObject.image.url.replace("images/", ""))
            image_path = os.path.join(settings.MEDIA_ROOT, imageObject.image.url)
            image = data.imread(image_path).astype(np.float64)

            image = self.preprocess_image(image, max_width, max_height)
            imsave(new_image_path, image)

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

    def standardization(self, image):
        return (image - np.mean(image)) / np.std(image)

    def preprocess_image(self, image, output_width, output_height):
        # Check if RGB image
        if len(image.shape) == 3:
            image = self.rgb2gray(image)

        image = self.standardization(image)
        image = resize(image, (output_width, output_height))

        return image