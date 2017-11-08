import os

import numpy
from PIL import Image
from django.core.management import BaseCommand

from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionQuery
from neural_network.nn_manager.DataGenerator import DataGenerator
from retina_scan import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print('Query Sequence NN')

        nn = SequenceDetectionQuery()
        datagen = DataGenerator(img_shape=nn.nn.input_shape)
        path = os.path.join(settings.MEDIA_ROOT, os.path.join('left_right_eye', os.path.join('test', 'left')))
        res = nn.model_predict(datagen.flow_from_directory(path))
        print(path)
        print('count: {}, left: {}, right: {}, nn: {}'.format(len(res), list(res.values()).count('L'), list(res.values()).count('R'), list(res.values()).count('N')))
