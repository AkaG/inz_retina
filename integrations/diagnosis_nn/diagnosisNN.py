from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.store.DBNNSave import DBNNSave
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten, Reshape, Input, Conv2D, BatchNormalization
from keras.layers.convolutional import Convolution1D, Convolution2D, MaxPooling2D
import keras.backend as K
from random import shuffle
import h5py
import numpy as np
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
np.random.seed(7)

class DiagnosisNN(TrainManager):
    def __init__(self):
        self.path_to_data = './prepared_data.hdf5'
        self.prepare_data(self.path_to_data)
        self.batch_size = 8
        self.epochs = 1
        super(DiagnosisNN, self).__init__()

    def prepare_data(self, path):
        hdf5_file = h5py.File(path, 'r')
        self.get_handlers(hdf5_file)
        self.load_sizes()

    def load_sizes(self):
        self.img_size_1 = self.X_train.shape[1]
        self.img_size_2 = self.X_train.shape[2]
        self.outputs_size = self.Y_train.shape[1]
        self.num_train_samples = self.X_train.shape[0]
        self.num_val_samples = self.X_val.shape[0]
        self.num_test_samples = self.X_test.shape[0]

    def get_handlers(self, file):
        self.X_train = file['train_data_x']
        self.Y_train = file['train_data_y']
        self.X_val = file['val_data_x']
        self.Y_val = file['val_data_y']
        self.X_test = file['test_data_x']
        self.Y_test = file['test_data_y']

    def store_method(self):
        return DBNNSave()

    def train_data_generator(self):
        generator = self._generator(self.X_train, self.Y_train)
        return generator

    def test_data_generator(self):
        generator = self._generator(self.X_val, self.Y_val)
        return generator

    def create_model(self):
        input_image = Input(shape=(self.img_size_1, self.img_size_2, 3))

        layer = Conv2D(filters=32, kernel_size=(3, 3))(input_image)
        layer = BatchNormalization(axis=1)(layer)
        layer = Activation('relu')(layer)
        layer = MaxPooling2D(pool_size=(2, 2))(layer)

        layer = Flatten()(layer)

        layer = Dense(self.outputs_size)(layer)
        layer = BatchNormalization(axis=1)(layer)
        output_layer = Activation('sigmoid')(layer)
        model = Model(inputs=input_image, outputs=output_layer)
        model.compile( optimizer='adam',
                       loss='binary_crossentropy',
                       metrics=[self.f1_score, self.precision, self.recall])
        return model

    def f1_score(self, y_true, y_pred):
        c1 = self.get_true_positive(y_true,y_pred)
        c2 = self.get_positive_pred(y_pred)
        c3 = self.get_positive_true(y_true)

        if c3 == 0:
            return 0

        precision = c1 / c2
        recall = c1 / c3
        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score

    def precision(self,y_true,y_pred):
        c1 = self.get_true_positive(y_true,y_pred)
        c2 = self.get_positive_pred(y_pred)
        return c1/c2

    def recall(self,y_true,y_pred):
        c1 = self.get_true_positive(y_true,y_pred)
        c3 = self.get_positive_true(y_true)
        return c1/c3

    def get_true_positive(self,y_true,y_pred):
        return K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))

    def get_positive_pred(self,y_pred):
        return K.sum(K.round(K.clip(y_pred, 0, 1)))

    def get_positive_true(self,y_true):
        return K.sum(K.round(K.clip(y_true, 0, 1)))

    def _generator(self,X,Y):
        while 1:
            batch_s = self.batch_size
            for i in range(X.shape[0] // self.batch_size):
                x_part = X[i*batch_s: (i+1)*batch_s]
                y_part = Y[i*batch_s: (i+1)*batch_s]
                yield x_part, y_part

    def train(self):
        self.train_model(
            self.num_train_samples // self.batch_size,
            self.num_val_samples // self.batch_size,
            epochs=self.epochs
        )


    #for tests

    def change_y_to_words(self,y):
        hdf5_file = h5py.File(self.path_to_data, 'r')
        n_gram = hdf5_file.attrs['n_gram']
        predicted_words = []
        for i in range(len(y)):
            if y[i] > 0.5:
                predicted_words.append(tuple(n_gram[i]))
        return predicted_words

    def get_model_quality(self, y_true,y_pred):
        c1 = sum(np.around(y_true*y_pred)) #TP
        c2 = sum(np.around(y_pred))
        c3 = sum(np.around(y_true))

        precision = c1/c2
        recall = c1 / c3
        f1_score = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f1_score

    def test_model(self):
        for i in range(len(self.X_test)):
            x_test = self.X_test[i:i+1]
            y_test = self.Y_test[i]
            y_score = self.model.predict(x_test)
            precision, recall, f1_score = self.get_model_quality(y_test,y_score[0])
            print("prec: %.2f, rec: %.2f, f1: %.2f" % (precision, recall, f1_score))
            #print(self.change_y_to_words(y_score[0]))