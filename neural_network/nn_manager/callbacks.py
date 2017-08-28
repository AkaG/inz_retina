import numpy as np
from keras.callbacks import Callback


class ModelSave(Callback):
    def __init__(self, nn_save_class, monitor='val_loss'):
        self.nn_save_class = nn_save_class
        self.monitor = monitor

        if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
            self.monitor_op = np.greater
            self.best = -np.Inf
        else:
            self.monitor_op = np.less
            self.best = np.Inf

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current = logs.get(self.monitor)
        if current is None:
            print('Can save best model only with %s available, '
                          'skipping.' % (self.monitor), RuntimeWarning)
        else:
            if self.monitor_op(current, self.best):
                self.best = current
                self.nn_save_class.save(self.model)
