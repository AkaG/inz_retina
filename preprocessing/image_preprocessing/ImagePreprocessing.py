import os

from data_module.models import ImageSeries, Image
from retina_scan import settings


class ImagePreprocessing():
    dir = os.path.join(settings.MEDIA_ROOT, "preprocessed")

    def __init__(self):
        self.create_dir()

    def create_dir(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
