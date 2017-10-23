from abc import abstractmethod


class AbstractDataGenerator(object):

    @abstractmethod
    def flow(self, files, names):
        pass

    @abstractmethod
    def flow_from_directory(self, path):
        pass
