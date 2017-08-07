import numpy as np
from skimage import data
from skimage.transform import resize
from sklearn import preprocessing


def rgb2gray(image):
    return np.dot(image[..., :3], [0.299, 0.587, 0.114])


def to_float(image):
    func = np.vectorize(lambda x: x / 255.0)

    return func(image)


def normalize(image):
    min_val = np.amin(image)
    max_val = np.amax(image)

    image -= np.amin(image)
    image /= (max_val - min_val)

    return image


def standardization(image):
    return (image - np.mean(image)) / np.std(image)


def preprocess_image(image, output_height, output_width, channel=0):
    image = image[:, :, channel]
    image = resize(image, (output_width, output_height))
    image = to_float(image)
    image = standardization(image)

    return image
