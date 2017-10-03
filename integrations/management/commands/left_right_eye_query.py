import os

import numpy
from PIL import Image
from django.core.management import BaseCommand

from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuery
from neural_network.nn_manager.DataGenerator import DataGenerator
from retina_scan import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print('Query Left Right Eye NN')

        nn = LeftRightEyeQuery()
        datagen = DataGenerator()
        path = os.path.join(settings.MEDIA_ROOT, os.path.join('left_right_eye', os.path.join('test', 'left')))
        res = nn.model_predict(datagen.flow_from_directory(path))
