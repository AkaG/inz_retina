from django.core.management import BaseCommand

from preprocessing.image_preprocessing.ImagePreprocessing import ImagePreprocessing


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print("Image preprocessing")

        ImagePreprocessing()