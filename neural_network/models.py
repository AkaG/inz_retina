from django.db import models


# Create your models here.

class NeuralNetwork(models.Model):
    model = models.FileField(
        upload_to="models/"
    )

    weights = models.FileField(
        upload_to="models_weights/"
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    val_loss = models.FloatField(
        null=True,
        blank=True
    )
    val_acc = models.FloatField(
        null=True,
        blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
