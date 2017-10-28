from django.core.management import BaseCommand

from integrations.sequence_detection_nn.SequenceDetectionQuery import SequenceDetectionQuery


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        nn = SequenceDetectionQuery()
        order_predicted, struct_result = nn.predict()
        print(order_predicted)