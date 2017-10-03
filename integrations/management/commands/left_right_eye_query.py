import os

import numpy
from PIL import Image
from django.core.management import BaseCommand

from integrations.left_right_eye_nn.LeftRightEyeQuery import LeftRightEyeQuery
from retina_scan import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print('Query Left Right Eye NN')

        nn = LeftRightEyeQuery()
        res = nn.model_predict(self.img_gen())
        print(res)

    def img_gen(self):
        path = os.path.join(settings.MEDIA_ROOT, os.path.join('left_right_eye', os.path.join('test', 'left')))
        for fname in os.listdir(path):
            if fname.endswith('.jpg'):
                print('append ' + fname)
                yield fname, Image.open(os.path.join(path, fname))