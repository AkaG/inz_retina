import numpy as np
from integrations.sequence_detection_nn.sequenceDetectionNN import SequenceDetectionNN

class SequenceDetectionQuery():
    def __init__(self):
        self.nn = SequenceDetectionNN()

    def get_test_sequences(self, pairs):
        sequences = []
        for pair in pairs:
            current_seq = pair['series']
            if current_seq not in sequences:
                sequences.append(current_seq)

        return sequences

    def create_sequence_pairs(self, images, names):
        pairs = []
        results_struct = {}
        for i in range(len(images)):
            for j in range(len(images)):
                if i == j:
                    continue
                pairs.append({'first':images[i],'first_name':names[i],'second':images[j], 'second_name':names[j]})
            results_struct[names[i]] = 0
        return pairs, results_struct

    def predict_pair(self,pair,results, sequence_detection):
        arr_img_1 = pair['first']
        arr_img_2 = pair['second']
        in_1 = np.array([arr_img_1])
        in_2 = np.array([arr_img_2])
        y_pred = sequence_detection.model.predict([in_1,in_2])
        y = y_pred.flatten()[0]
        results[pair['first_name']] = results[pair['first_name']] + y
        results[pair['second_name']] = results[pair['second_name']] + (1-y)

    def get_tau(self,results):
        sorted_result = sorted(results.items(), key=lambda x:x[1])
        order_predicted = []
        for item in sorted_result:
            key,value = item
            order_predicted.append(key)
        return order_predicted

    def prepare_images(self,images):
        prepared_images = []
        prepared_names = []
        for img in images:
            prepared_images.append(self.nn._prepare_image(img,True))
            prepared_names.append(img.name)
        return prepared_images, prepared_names

    def predict(self,images):
        prepared_images, names = self.prepare_images(images)
        with self.nn.graph.as_default():
            pairs, results_struct = self.create_sequence_pairs(prepared_images, names)
            for pair in pairs:
                self.predict_pair(pair,results_struct,self.nn)
            order_predicted = self.get_tau(results_struct)
            return order_predicted, results_struct

class SequenceDetectionNNSingleton(object):
    query = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.query is None:
            cls.query = SequenceDetectionQuery()
        return cls.query
