import tempfile
from typing import List

from keras import callbacks

from retina_scan import settings


class TrainManager(object):
    """
    Abstract class to train NN implement model and generators
    Set parameters
    """

    def __init__(self):
        self.model = self.create_model()

    def generate_callbacks(self, directory) -> List:
        return [
            callbacks.ModelCheckpoint(directory, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1),
            callbacks.EarlyStopping(monitor='val_loss', min_delta=0.01, patience=5, verbose=0, mode='auto')
        ]

    def train_model(self, steps_per_epoch, validation_steps, epochs=5):
        with tempfile.TemporaryDirectory(dir=settings.MEDIA_ROOT) as temp_dir:
            history = self._model.fit_generator(
                self.train_data_generator(),
                steps_per_epoch=steps_per_epoch,
                epochs=epochs,
                validation_data=self.test_data_generator(),
                validation_steps=validation_steps,
                callbacks=self.generate_callbacks(temp_dir)
            )

            self.save_model()
            self.save_best_weights(temp_dir)

    def save_model(self):
        # TODO
        pass

    def save_best_weights(self, directory):
        # TODO
        pass

    def create_model(self):
        pass

    def train_data_generator(self):
        pass

    def test_data_generator(self):
        pass
