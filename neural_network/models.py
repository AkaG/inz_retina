from django.db import models


# Create your models here.

class NeuralNetwork(models.Model):
    model = models.FileField(
        upload_to="/models"
    )

    weights = models.FileField(
        upload_to="/models_weights"
    )

    description = models.TextField()
