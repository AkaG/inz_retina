from django.db import models

from neural_network.models import NeuralNetwork


class Report(models.Model):
    report = models.FileField(
        upload_to="/reports",
        blank=True,
        null=True
    )

    neural_network = models.ForeignKey(
        NeuralNetwork,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
