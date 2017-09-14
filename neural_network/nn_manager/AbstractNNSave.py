from abc import abstractmethod


class AbstractNNSave(object):
    def __init__(self):
        self.kwargs = None

    def save(self, model, **kwargs):
        self.kwargs = kwargs
        self.save_model(model)
        self.save_weights(model)

    @abstractmethod
    def save_model(self, model):
        pass

    @abstractmethod
    def save_weights(self, model):
        pass
