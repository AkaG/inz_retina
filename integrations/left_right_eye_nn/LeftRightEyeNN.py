import os
import shutil

from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator

from data_module.models import ImageSeries, Image
from neural_network.nn_manager.FileNNSave import FileNNSave
from neural_network.nn_manager.DBNNSave import DBNNSave
from neural_network.nn_manager.TrainManager import TrainManager
from retina_scan import settings


class LeftRightEyeNN(TrainManager):
    input_shape = (100, 100, 3)

    batch_size = 4
    epochs = 2
    steps_per_epoch = 20
    validation_steps = 20

    dir = os.path.join(settings.MEDIA_ROOT, "left_right_eye")
    train_dir = os.path.join(dir, "train")
    test_dir = os.path.join(dir, "test")

    left_eye_folder = "left"
    right_eye_folder = "right"

    def __init__(self):
        super(LeftRightEyeNN, self).__init__()

        self.create_dirs()

    def create_dirs(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        if not os.path.isdir(self.train_dir):
            os.makedirs(self.train_dir)
        if len(os.listdir(self.train_dir)) == 0:
            os.makedirs(os.path.join(self.train_dir, self.left_eye_folder))
            os.makedirs(os.path.join(self.train_dir, self.right_eye_folder))

        if not os.path.isdir(self.test_dir):
            os.makedirs(self.test_dir)
        if len(os.listdir(self.test_dir)) == 0:
            os.makedirs(os.path.join(self.test_dir, self.left_eye_folder))
            os.makedirs(os.path.join(self.test_dir, self.right_eye_folder))

    def create_model(self):
        model = Sequential()

        model.add(Convolution2D(128, (3, 3), activation='relu', input_shape=self.input_shape))
        # model.add(MaxPooling2D(pool_size=(2, 2)))
        # model.add(Convolution2D(128, (3, 3), activation='relu'))
        model.add(Flatten())
        # model.add(Dense(512, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
        return model

    def test_data_generator(self):
        return self.data_gen().flow_from_directory(
            self.test_dir,
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=self.batch_size,
            class_mode='binary'
        )

    def train_data_generator(self):
        return self.data_gen().flow_from_directory(
            self.train_dir,
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=self.batch_size,
            class_mode='binary'
        )

    @staticmethod
    def data_gen():
        return ImageDataGenerator(
            rescale=1. / 255
        )

    def store_method(self):
        return DBNNSave()

    def generate_data(self):
        if len(os.listdir(os.path.join(self.train_dir, self.left_eye_folder))) == 0:
            print("left eye images folder empty - generating data")
            train_left = os.path.join(self.train_dir, self.left_eye_folder)
            test_left = os.path.join(self.test_dir, self.left_eye_folder)

            left_img = Image.objects.all().filter(image_series__eye=ImageSeries.LEFT)
            for img in left_img:
                shutil.copy2(img.image.path, train_left)
                shutil.copy2(img.image.path, test_left)

        if len(os.listdir(os.path.join(self.train_dir, self.right_eye_folder))) == 0:
            print("right eye images folder empty - generating data")
            train_right = os.path.join(self.train_dir, self.right_eye_folder)
            test_right = os.path.join(self.test_dir, self.right_eye_folder)

            right_img = Image.objects.all().filter(image_series__eye=ImageSeries.RIGHT)
            for img in right_img:
                shutil.copy2(img.image.path, train_right)
                shutil.copy2(img.image.path, test_right)

    def train(self):
        self.train_model(
            self.steps_per_epoch // self.batch_size,
            self.validation_steps // self.batch_size,
            epochs=self.epochs
        )