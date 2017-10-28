from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.store.DBNNSave import DBNNSave
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Flatten, Reshape, Input, Conv2D, BatchNormalization
from keras.layers.convolutional import Convolution1D, Convolution2D, MaxPooling2D
import keras
from data_module.models import Person, Examination, Description, ImageSeries
from data_module.models import Image as Retina_Image
from random import shuffle
import random, re, PIL
import numpy as np
from skimage.transform import resize
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model

width = 1388
height = 1038

img_size_2 = 160
img_size_1 = int(img_size_2 * (height / width))


class SequenceDetectionNN(TrainManager):
    def __init__(self, train=False):
        if train:
            super(SequenceDetectionNN, self).__init__()
            self._init_data()
        else:
            self.model = load_model('sequence_model_size150.hd5')

    def store_method(self):
        return DBNNSave()

    def train_data_generator(self):
        generator = self._generator(self.first_img_arr_train, self.second_img_arr_train, self.y_train_p,
                                    self.batch_size, self.datagen, do_shuffle=False)
        return generator

    # TODO: change for val_data_generator
    def test_data_generator(self):
        generator = self._generator(self.first_img_arr_val, self.second_img_arr_val, self.y_val_p, self.batch_size,
                                    self.datagen_val, do_shuffle=False)
        return generator

    def create_model(self):
        input_image_1 = Input(shape=(img_size_1, img_size_2, 1))
        input_image_2 = Input(shape=(img_size_1, img_size_2, 1))
        merged_vector = keras.layers.concatenate([input_image_1, input_image_2], axis=-1)

        layer = Conv2D(filters=32, kernel_size=(3, 3))(merged_vector)
        layer = BatchNormalization(axis=1)(layer)
        layer = Activation('relu')(layer)
        layer = MaxPooling2D(pool_size=(2, 2))(layer)

        layer = Conv2D(filters=64, kernel_size=(3, 3))(layer)
        layer = BatchNormalization(axis=1)(layer)
        layer = Activation('relu')(layer)
        layer = MaxPooling2D(pool_size=(2, 2))(layer)

        layer = Flatten()(layer)

        layer = Dense(1024)(layer)
        layer = BatchNormalization(axis=1)(layer)
        layer = Activation('relu')(layer)

        layer = Dense(64)(layer)
        layer = BatchNormalization(axis=1)(layer)
        layer = Activation('relu')(layer)

        layer = Dense(1)(layer)
        layer = BatchNormalization(axis=1)(layer)
        output_layer = Activation('sigmoid')(layer)
        model = Model(inputs=[input_image_1, input_image_2], outputs=output_layer)
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

    def _init_data(self):
        train_samples, val_samples, test_samples = self._split_data()
        self.train_pairs_first, self.train_pairs_second, self.y_train_p, self.train_pairs = self._get_pairs(
            train_samples)
        self.val_pairs_first, self.val_pairs_second, self.y_val_p, _ = self._get_pairs(val_samples)
        self.test_pairs_first, self.test_pairs_second, self.y_test_p, self.test_pairs = self._get_pairs(test_samples)

        self.first_img_arr_train, self.second_img_arr_train = self._get_data(self.train_pairs_first,
                                                                             self.train_pairs_second)
        self.first_img_arr_val, self.second_img_arr_val = self._get_data(self.val_pairs_first, self.val_pairs_second)

        self.nb_train_samples = int(len(self.train_pairs_first))
        self.nb_val_samples = int(len(self.val_pairs_first))
        self.nb_test_samples = int(len(self.test_pairs_first))
        self.batch_size = 16
        self.epochs = 100

        self.datagen = ImageDataGenerator(
            shear_range=0.2,
            zoom_range=0.2,
            vertical_flip=True,
            horizontal_flip=True,
            rotation_range=30
        )

        self.datagen_val = ImageDataGenerator()

    def _get_data(self, pairs_first, pairs_second):
        first_img_arr = []
        second_img_arr = []
        first_prepared = dict()
        second_prepared = dict()

        for p1, p2 in zip(pairs_first, pairs_second):
            if p1 in first_prepared:
                arr_img_1 = first_prepared[p1]
            else:
                img1 = Retina_Image.objects.filter(id=p1)[0]
                arr_img_1 = self._prepare_image(img1)
                first_prepared[p1] = arr_img_1

            if p2 in second_prepared:
                arr_img_2 = second_prepared[p2]
            else:
                img2 = Retina_Image.objects.filter(id=p2)[0]
                arr_img_2 = self._prepare_image(img2)
                second_prepared[p2] = arr_img_2

            first_img_arr.append(arr_img_1)
            second_img_arr.append(arr_img_2)

        first_prepared = None
        second_prepared = None
        first_img_arr = np.array(first_img_arr)
        second_img_arr = np.array(second_img_arr)
        return first_img_arr, second_img_arr

    def _generator(self, first_img_arr, second_img_arr, y_arr, batch_size, datagen, do_shuffle=True, file=None):
        batches = datagen.flow(first_img_arr, y_arr, batch_size=batch_size, shuffle=False)
        batches2 = datagen.flow(second_img_arr, y_arr, batch_size=batch_size, shuffle=False)
        while 1:
            for batch_1, batch_2 in zip(batches, batches2):
                yield [batch_1[0], batch_2[0]], batch_1[1]

    def _prepare_image(self, img):
        img = PIL.Image.open(img.image).convert('L')
        arr_img = np.array(img)
        arr_img = self.preprocess_image(arr_img, img_size_1, img_size_2)
        return arr_img

    def _get_pairs(self, examinations, do_shuffle=True):
        pairs = []
        for examin in examinations:
            sequences = ImageSeries.objects.filter(examination=examin)
            for i in range(len(sequences)):
                if sequences[i].name.endswith("after_registration"):
                    continue
                imgModels = Retina_Image.objects.filter(image_series=sequences[i])
                for j in range(len(imgModels)):
                    for k in range(len(imgModels) - 1):
                        if j <= k:
                            continue
                        number1 = int(re.search(r'\d+', imgModels[j].name).group())
                        number2 = int(re.search(r'\d+', imgModels[k].name).group())
                        result = number1 > number2
                        y_train = 0
                        if (result):
                            y_train = 1
                        w = random.randint(0, 1)
                        if (w == 1):
                            pairs.append(
                                {'series': sequences[i].id, 'first': imgModels[j].id, 'second': imgModels[k].id,
                                 'y_train': y_train})
                        elif (w == 0):
                            pairs.append(
                                {'series': sequences[i].id, 'first': imgModels[k].id, 'second': imgModels[j].id,
                                 'y_train': 1 - y_train})
        if (do_shuffle):
            shuffle(pairs)
        first = []
        second = []
        y = []
        for pair in pairs:
            first.append(pair['first'])
            second.append(pair['second'])
            y.append(pair['y_train'])
        return first, second, y, pairs

    def _get_examinations_part(self, start, end, persons):
        examinations_part = []
        for person in persons[start:end]:
            examinations = Examination.objects.filter(person=person)
            for examin in examinations:
                examinations_part.append(examin)
        return examinations_part

    def _split_data(self, fraction=0.6):
        persons = list(Person.objects.all())
        shuffle(persons)
        nb_persons_train = round(len(persons) * fraction)
        nb_other = len(persons) - nb_persons_train
        if nb_other % 2 == 0:
            nb_persons_val = int(nb_other / 2)
        else:
            nb_persons_val = int(nb_other / 2 - 1)

        train_examinations = self._get_examinations_part(0, nb_persons_train, persons)
        val_examinations = self._get_examinations_part(nb_persons_train, nb_persons_train + nb_persons_val, persons)
        test_examinations = self._get_examinations_part(nb_persons_train + nb_persons_val, len(persons), persons)

        return train_examinations, val_examinations, test_examinations

    def train(self):
        self.train_model(
            self.nb_train_samples // self.batch_size,
            self.nb_val_samples // self.batch_size,
            epochs=self.epochs
        )

    def to_float(self, image):
        func = np.vectorize(lambda x: x / 255.0)
        return func(image)

    def standardization(self, image):
        return (image - np.mean(image)) / np.std(image)

    def preprocess_image(self, image, size_1, size_2, channel=0):
        image = resize(image, (size_1, size_2, 1))
        image = self.to_float(image)
        image = self.standardization(image)

        return image
