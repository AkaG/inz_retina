import numpy as np


def image_to_float(image):
    func = np.vectorize(lambda x: x / 255.0)

    return func(image)


def image_normalize(image):
    minval = np.amin(image)
    maxval = np.amax(image)

    image -= np.amin(image)
    image /= (maxval - minval)

    return image


def preprocess_image(image, output_height, output_width):
    image = image_to_float(image)
    image = image_normalize(image)