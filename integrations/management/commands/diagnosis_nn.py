from django.core.management import BaseCommand

from integrations.diagnosis_nn.diagnosisNN import DiagnosisNN


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print("Training diagnosiss nn")
        nn = DiagnosisNN()
        nn.train()
        nn.test_model()