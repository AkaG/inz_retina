from django.core.management import BaseCommand

"""
Command for loading data from disc to database
"""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        for path in options['path']:
            self.load_data_from_path(path)

    def load_data_from_path(self, path):
        print("Loading data from %s" % path)
