from django.core.management import BaseCommand

from integrations.left_right_eye_nn.LeftRightEyeNN import LeftRightEyeNN


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.main()

    def main(self):
        print("Training Left Right Eye NN")

        nn = LeftRightEyeNN()
        nn.generate_data()
        nn.train()