from django.core.management import BaseCommand

from preprocessing.image_preprocessing.ImagePreprocessing import ImagePreprocessing


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('width', default=0, type=int, nargs='?')
        parser.add_argument('height', default=0, type=int, nargs='?')

    def handle(self, *args, **options):
        self.main(options)

    def main(self, options):
        print("Image preprocessing")

        ImagePreprocessing(options['width'], options['height'])