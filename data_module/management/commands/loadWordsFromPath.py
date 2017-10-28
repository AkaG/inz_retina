from django.core.management import BaseCommand

from data_module.data_acquire.words_path_loader import WordsPathLoader


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        for path in options['path']:
            self.load_words_from_path(path)

    def load_words_from_path(self, path):
        words_path_loader = WordsPathLoader(path)
        words_path_loader.load_words()
