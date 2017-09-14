import os
import shutil

from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Activation
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator

from data_module.models import ImageSeries, Image, Person, Examination
from neural_network.models import NeuralNetwork
from neural_network.nn_manager.DBNNSave import DBNNSave
from neural_network.nn_manager.ModelLoader import load_weights_from_file
from neural_network.nn_manager.TrainManager import TrainManager
from retina_scan import settings


class LeftRightEyeNN(TrainManager):
    input_shape = (100, 100, 3)

    batch_size = 32
    epochs = 50
    steps_per_epoch = 2000
    validation_steps = 700

    db_description = 'left_right_eye'

    dir = os.path.join(settings.MEDIA_ROOT, "left_right_eye")
    train_dir = os.path.join(dir, "train")
    validation_dir = os.path.join(dir, "validate")
    test_dir = os.path.join(dir, "test")

    left_eye_folder = "left"
    right_eye_folder = "right"

    def __init__(self):
        super(LeftRightEyeNN, self).__init__()

        self.create_dirs()

    def create_dirs(self):

        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

        self._create_dir(self.train_dir)
        self._create_dir(self.validation_dir)
        self._create_dir(self.test_dir)

    def _create_dir(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        if len(os.listdir(path)) == 0:
            os.makedirs(os.path.join(path, self.left_eye_folder))
            os.makedirs(os.path.join(path, self.right_eye_folder))

    def create_model(self):
        model = Sequential()

        model.add(Convolution2D(128, (3, 3), input_shape=self.input_shape))
        model.add(BatchNormalization())
        model.add(Activation('relu'))

        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(BatchNormalization())

        model.add(Convolution2D(128, (3, 3)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))

        model.add(MaxPooling2D(pool_size=(3, 3)))
        model.add(Flatten())

        model.add(Dense(128))
        model.add(BatchNormalization())
        model.add(Activation('relu'))

        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])

        nn = NeuralNetwork.objects.all().filter(description=self.db_description)
        if nn.count() > 0:
            nn = nn.latest('created')
            load_weights_from_file(model=model, file_path=nn.weights.path)

        print(model.summary())
        return model

    def test_data_generator(self):
        return self.data_gen().flow_from_directory(
            self.validation_dir,
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
        return DBNNSave(description=self.db_description)

    def generate_data(self):
        train_factor = 0.8
        validation_factor = 0.15

        patients = Person.objects.all()
        patient_count = patients.count()

        if len(os.listdir(os.path.join(self.train_dir, self.left_eye_folder))) == 0:
            print("generating train data")
            train_left = os.path.join(self.train_dir, self.left_eye_folder)
            train_right = os.path.join(self.train_dir, self.right_eye_folder)
            for patient in patients[:(patient_count * train_factor)]:
                self._generate_data_from_patient(patient, train_left, train_right)

        if len(os.listdir(os.path.join(self.validation_dir, self.left_eye_folder))) == 0:
            print("generating validation data")
            validation_left = os.path.join(self.validation_dir, self.left_eye_folder)
            validation_right = os.path.join(self.validation_dir, self.right_eye_folder)
            for patient in patients[(patient_count * train_factor):(patient_count * (train_factor + validation_factor))]:
                self._generate_data_from_patient(patient, validation_left, validation_right)

        if len(os.listdir(os.path.join(self.test_dir, self.left_eye_folder))) == 0:
            print("generating test data")
            test_left = os.path.join(self.test_dir, self.left_eye_folder)
            test_right = os.path.join(self.test_dir, self.right_eye_folder)
            for patient in patients[(patient_count * (train_factor + validation_factor)):]:
                self._generate_data_from_patient(patient, test_left, test_right)

    def _generate_data_from_patient(self, patient, img_left_path, img_right_path):
        exams = Examination.objects.all().filter(person=patient)
        for exam in exams:
            for img_serie in ImageSeries.objects.all().filter(examination=exam, eye=ImageSeries.LEFT):
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_left_path)
            for img_serie in ImageSeries.objects.all().filter(examination=exam, eye=ImageSeries.RIGHT):
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_right_path)

    @staticmethod
    def _copy_queryset_images_to_path(qs, path):
        for img in qs:
            shutil.copy2(img.image.path, path)

    def train(self):
        self.train_model(
            self.steps_per_epoch // self.batch_size,
            self.validation_steps // self.batch_size,
            epochs=self.epochs,
            save_at_end=False
        )
