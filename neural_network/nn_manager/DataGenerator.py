from neural_network.nn_manager.AbstractDataGenerator import AbstractDataGenerator


class DataGenerator(AbstractDataGenerator):
    def flow_from_directory(self, path):
        pass

    def flow(self, files, names):
        for file, name in zip(files, names):
            yield name, file
