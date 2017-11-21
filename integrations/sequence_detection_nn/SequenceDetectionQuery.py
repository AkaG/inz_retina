import numpy as np
from scipy.stats import kendalltau
import re
from integrations.sequence_detection_nn.sequenceDetectionNN import SequenceDetectionNN
from data_module.models import Image as Retina_Image
from data_module.models import Person, Examination, Description, ImageSeries


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

    def create_sequence_pairs(self, _image_series):
        images = Retina_Image.objects.filter(image_series = _image_series)
        pairs = []
        results_struct = {}
        for i in range(len(images)):
            for j in range(len(images)):
                if i == j:
                    continue
                pairs.append({'first':images[i],'second':images[j]})
            results_struct[images[i].name] = 0
        return pairs, results_struct

    def predict_pair(self,pair,results, sequence_detection):
        img1 = pair['first']
        img2 = pair['second']
        arr_img_1 = sequence_detection._prepare_image(img1)
        arr_img_2 = sequence_detection._prepare_image(img2)
        in_1 = np.array([arr_img_1])
        in_2 = np.array([arr_img_2])
        y_pred = sequence_detection.model.predict([in_1,in_2])
        y = y_pred.flatten()[0]
        results[img1.name] = results[img1.name] + y
        results[img2.name] = results[img2.name] + (1-y)

    def get_tau(self,results):
        sorted_result = sorted(results.items(), key=lambda x:x[1])
        order_predicted = []
        order_original = []
        j = 0
        for item in sorted_result:
            key,value = item
            predicted_number_name = int(re.search(r'\d+', key).group())
            order_predicted.append(predicted_number_name)
            order_original.append(j)
            j = j + 1
        #tau, p_value = kendalltau(order_original, order_predicted)
        return order_predicted

    def predict(self):
        series = ImageSeries.objects.all()[0]
        pairs, results_struct = self.create_sequence_pairs(series)
        for pair in pairs:
            self.predict_pair(pair,results_struct,self.nn)
        order_predicted = self.get_tau(results_struct)
        return order_predicted, results_struct

    def create_sequence_pairs(self,_image_series):
        images = Retina_Image.objects.filter(image_series = _image_series)
        pairs = []
        results_struct = {}
        for i in range(len(images)):
            for j in range(len(images)):
                if i == j:
                    continue
                pairs.append({'first':images[i],'second':images[j]})
            results_struct[images[i].name] = 0
        return pairs, results_struct


class SequenceDetectionNNSingleton(object):
    query = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.query is None:
            cls.query = SequenceDetectionQuery()
        return cls.query
