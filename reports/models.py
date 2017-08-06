from django.db import models

class Report(models.Model):
    report = models.FileField()
    weights = models.FileField()
    model = models.FileField()
