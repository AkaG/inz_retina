from django.core.management import BaseCommand

from integrations.sequence_detection_nn.sequenceDetectionNN import SequenceDetectionNN


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        nn = SequenceDetectionNN()
        nn.train()