from abc import abstractmethod


class AbstractNNSave(object):
    def save(self, model):
        self.save_model(model)
        self.save_weights(model)

    @abstractmethod
    def save_model(self, model):
        pass

    @abstractmethod
    def save_weights(self, model):
        pass