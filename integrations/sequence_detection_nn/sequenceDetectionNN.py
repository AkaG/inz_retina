from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.models import NeuralNetwork
from keras.models import load_model
from keras import backend as K
from skimage.transform import resize
import tensorflow as tf
import numpy as np
import PIL


class SequenceDetectionNN(TrainManager):
    def __init__(self):
        self.load_image_resolution()
        nn = NeuralNetwork.objects.get(model="models/sd_model-150.h5")
        self.sess = tf.Session()
        K.set_session(self.sess)
        self.model = load_model(nn.model.path)

    def load_image_resolution(self):
        width = 1388
        height = 1038
        self.img_size_2 = 150
        self.img_size_1 = int(self.img_size_2 * (height / width))

    def _prepare_image(self,img):
        img = PIL.Image.open(img).convert('L')
        arr_img = self.preprocess_image(img)
        return arr_img 

    def standardization(self,image):
        return (image - np.mean(image)) / np.std(image)
    
    def preprocess_image(self,image):
        image = np.array(image)
        image = self.standardization(image)
        image = resize(image, (self.img_size_1, self.img_size_2, 1))
        return image