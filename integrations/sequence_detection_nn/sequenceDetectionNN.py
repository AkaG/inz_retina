from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.nn_manager.DBNNSave import DBNNSave
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten, Reshape, Input, Conv2D, BatchNormalization
from keras.layers.convolutional import Convolution1D, Convolution2D, MaxPooling2D
import keras
from data_module.models import Person, Examination, Description, ImageSeries
from data_module.data_acquire.path_loader import PathLoader
from data_module.models import Image as Retina_Image
from random import shuffle
import random, re, PIL
import numpy as np
from skimage.transform import resize


img_size_1 = 120
img_size_2 = 150
class SequenceDetectionNN(TrainManager):

    def __init__(self):
        super(SequenceDetectionNN, self).__init__()

        train_samples, test_samples = self._split_data()
        self.train_pairs = self._get_pairs(train_samples)
        self.test_pairs = self._get_pairs(test_samples)
        self.nb_train_samples = int(len(self.train_pairs)/10)
        self.nb_test_samples = int(len(self.test_pairs)/10)
        self.batch_size = 32
        self.epochs = 20


    def store_method(self):
        return DBNNSave()

    def train_data_generator(self):
        generator = self._generator(self.train_pairs,self.batch_size)
        return generator

    def test_data_generator(self):
        generator = self._generator(self.test_pairs,self.batch_size)
        return generator

    def create_model(self):
        input_image_1 = Input(shape=(img_size_1,img_size_2,1))
        input_image_2 = Input(shape=(img_size_1,img_size_2,1))
        merged_vector = keras.layers.concatenate([input_image_1, input_image_2], axis=-1)

        conv2d_1 = Conv2D(filters=32,kernel_size=(3,3))(merged_vector)
        batch_norm_1 = BatchNormalization(axis=1)(conv2d_1)
        activation_1 = Activation('relu')(batch_norm_1)
        max_pooling_1 = MaxPooling2D(pool_size=(2,2))(activation_1)

        flatten = Flatten()(max_pooling_1)
        dense_1 = Dense(128)(flatten)
        batch_norm_2 = BatchNormalization(axis=1)(dense_1)
        activation_2 = Activation('relu')(batch_norm_2)

        dense_2 = Dense(1)(activation_2)
        batch_norm_3 = BatchNormalization(axis=1)(dense_2)
        activation_3 = Activation('sigmoid')(batch_norm_3)


        model = Model(inputs=[input_image_1,input_image_2],outputs=activation_3)
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model


    def _generator(self,pairs,batch_size):
        while 1:
            shuffle(pairs)
            for i in range(int(len(pairs) / batch_size)):

                x1_train = []; x2_train = []; y_train = []

                for j in range(batch_size):
                    img1 = Retina_Image.objects.filter(image_series = pairs[i*batch_size+j]['series'], id=pairs[i*batch_size+j]['first'])[0]
                    img2 = Retina_Image.objects.filter(image_series = pairs[i*batch_size+j]['series'], id=pairs[i*batch_size+j]['second'])[0]

                    arr_img_1 = self._prepare_image(img1)
                    arr_img_2 = self._prepare_image(img2)

                    y_train.append(np.array([pairs[i*batch_size+j]['y_train']]))
                    x1_train.append(np.array(arr_img_1))
                    x2_train.append(np.array(arr_img_2))

                x1_train = np.array(x1_train)
                x2_train = np.array(x2_train)
                y_train = np.array(y_train)

                yield [x1_train,x2_train], y_train


    def _prepare_image(self,img):
        img = PIL.Image.open(img.image).convert('L')
        arr_img = np.array(img)
        arr_img = self.preprocess_image(arr_img,img_size_1,img_size_2)
        return arr_img


    def _get_pairs(self,examinations):
        pairs = []
        for examin in examinations:
            sequences = ImageSeries.objects.filter(examination = examin)
            for i in range(len(sequences)):
                imgModels = Retina_Image.objects.filter(image_series = sequences[i])
                for j in range(len(imgModels)):
                    for k in range(len(imgModels)-1):
                        if j <= k:
                            continue
                        number1 = int(re.search(r'\d+', imgModels[j].name).group())
                        number2 = int(re.search(r'\d+', imgModels[k].name).group())
                        result = number1 > number2
                        y_train = 0
                        if(result):
                            y_train = 1
                        w = random.randint(0, 1)
                        if(w):
                            pairs.append({'series':sequences[i].id, 'first':imgModels[j].id, 'second':imgModels[k].id, 'y_train':y_train})
                        else:
                            pairs.append({'series':sequences[i].id, 'first':imgModels[k].id, 'second':imgModels[j].id, 'y_train':1-y_train})
        shuffle(pairs)
        return pairs


    def _split_data(self,fraction=0.8):
        examinations = Examination.objects.all()
        nb_train_exams = round(len(examinations)*fraction)
        train_samples = examinations[0:nb_train_exams]
        test_samples = examinations[nb_train_exams:len(examinations)]
        return train_samples, test_samples


    def train(self):
        self.train_model(
            self.nb_train_samples // self.batch_size,
            self.nb_test_samples // self.batch_size,
            epochs=self.epochs
        )


    def to_float(self,image):
        func = np.vectorize(lambda x: x / 255.0)

        return func(image)


    def standardization(self,image):
        return (image - np.mean(image)) / np.std(image)


    def preprocess_image(self,image, size_1, size_2, channel=0):
        #image = image[:, :, channel]
        image = resize(image, (size_1, size_2,1))
        image = self.to_float(image)
        image = self.standardization(image)

        return image