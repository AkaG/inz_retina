from django.core.management import BaseCommand

"""
Main method for executing without running server
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print("hello world")
