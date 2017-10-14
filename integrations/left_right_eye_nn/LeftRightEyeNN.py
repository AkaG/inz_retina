import os
import shutil

from PIL import Image as PILImage
from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Activation
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator

from data_module.models import ImageSeries, Image, Person, Examination
from neural_network.models import NeuralNetwork
from neural_network.nn_manager.TrainManager import TrainManager
from neural_network.store.DBNNSave import DBNNSave
from neural_network.store.ModelLoader import load_weights_from_file
from retina_scan import settings


class LeftRightEyeNN(TrainManager):
    input_shape = (100, 100, 1)

    batch_size = 32
    epochs = 50
    steps_per_epoch = 4000
    validation_steps = 900

    db_description = 'left_right_eye3'

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
            class_mode='binary',
            color_mode='grayscale'
        )

    def train_data_generator(self):
        return self.data_gen().flow_from_directory(
            self.train_dir,
            target_size=(self.input_shape[0], self.input_shape[1]),
            batch_size=self.batch_size,
            class_mode='binary',
            color_mode='grayscale'
        )

    @staticmethod
    def data_gen():
        return ImageDataGenerator(
            rescale=1. / 255
        )

    def store_method(self):
        return DBNNSave(description=self.db_description)

    def generate_data(self):
        train_factor = 0.75
        validation_factor = 0.15

        self._generate_single_set(self.train_dir, start_factor=0, end_factor=train_factor)
        self._generate_single_set(self.validation_dir, start_factor=train_factor, end_factor=train_factor + validation_factor)
        self._generate_single_set(self.test_dir, start_factor=train_factor + validation_factor, end_factor=1)

    def _generate_single_set(self, path, start_factor=0, end_factor=1):
        patients = Person.objects.all()
        patient_count = patients.count()

        if len(os.listdir(os.path.join(path, self.left_eye_folder))) == 0:
            print("generating data into {}".format(path))
            left_dir = os.path.join(path, self.left_eye_folder)
            right_dir = os.path.join(path, self.right_eye_folder)
            for patient in patients[(patient_count * start_factor):(patient_count * end_factor)]:
                self._generate_data_from_patient(patient, left_dir, right_dir)

    def _generate_data_from_patient(self, patient, img_left_path, img_right_path):
        exams = Examination.objects.all().filter(person=patient)
        for exam in exams:
            for img_serie in ImageSeries.objects.all().filter(examination=exam, eye=ImageSeries.LEFT).exclude(name__icontains='after'):
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_left_path)
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_right_path,
                                                   preprocess_func=self._transform_image)
            for img_serie in ImageSeries.objects.all().filter(examination=exam, eye=ImageSeries.RIGHT).exclude(name__icontains='after'):
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_right_path)
                self._copy_queryset_images_to_path(Image.objects.all().filter(image_series=img_serie), img_left_path,
                                                   preprocess_func=self._transform_image)

    def _copy_queryset_images_to_path(self, qs, path, preprocess_func=None):
        for img in qs:
            if preprocess_func is None:
                shutil.copy2(img.image.path, path)
            else:
                pilimg = PILImage.open(img.image.path)
                pilimg = preprocess_func(pilimg)
                pilimg.save(self._prepare_name(path, img.image.name.split('/')[-1]))

    @staticmethod
    def _prepare_name(path, img_name, extension='_1'):
        img_name = img_name.split('.')
        return os.path.join(path, '{}{}.{}'.format(img_name[0], extension, img_name[1]))

    @staticmethod
    def _transform_image(img):
        return img.transpose(PILImage.FLIP_LEFT_RIGHT)

    def train(self):
        self.train_model(
            self.steps_per_epoch // self.batch_size,
            self.validation_steps // self.batch_size,
            epochs=self.epochs,
            save_at_end=False
        )
