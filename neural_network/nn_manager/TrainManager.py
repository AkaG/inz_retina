import tempfile
from abc import abstractmethod
from typing import List

from keras import callbacks

from neural_network.nn_manager.AbstractNNSave import AbstractNNSave
from neural_network.nn_manager.callbacks import ModelSave
from retina_scan import settings


class TrainManager(object):
    """
    Abstract class to train NN implement model and generators
    Set parameters
    """

    def __init__(self):
        self.model = self.create_model()
        self.nn_save_class = self.store_method()

    def default_callbacks(self, directory) -> List:
        return [
            # callbacks.ModelCheckpoint(os.path.join(directory, 'weights.{epoch:02d}-{val_loss:.2f}.hdf5'), monitor='val_loss', verbose=0,
            #                           save_best_only=True, save_weights_only=True, mode='auto', period=1),
            callbacks.EarlyStopping(monitor='val_loss', min_delta=0.01, patience=5, verbose=0, mode='auto'),
            ModelSave(self.nn_save_class),
        ]

    def train_model(self, steps_per_epoch, validation_steps, epochs=5):
        with tempfile.TemporaryDirectory(dir=settings.MEDIA_ROOT) as temp_dir:
            history = self.model.fit_generator(
                self.train_data_generator(),
                steps_per_epoch=steps_per_epoch,
                epochs=epochs,
                validation_data=self.test_data_generator(),
                validation_steps=validation_steps,
                callbacks=self.default_callbacks(temp_dir)
            )

            self.nn_save_class.save(self.model)

    @abstractmethod
    def store_method(self) -> AbstractNNSave:
        pass

    @abstractmethod
    def create_model(self):
        pass

    @abstractmethod
    def train_data_generator(self):
        pass

    @abstractmethod
    def test_data_generator(self):
        pass
