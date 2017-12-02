from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.models import NeuralNetwork
import tensorflow as tf
from keras.models import load_model
from keras import backend as K

class SequenceDetectionNN(TrainManager):
    def __init__(self):
        nn = NeuralNetwork.objects.get(model="models/sequence_model_size150.hd5")
        self.model = load_model(nn.model.path)
        self.sess = tf.Session()
        K.set_session(self.sess)
