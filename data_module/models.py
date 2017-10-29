from django.db import models


# Create your models here.

class Person(models.Model):
    code_name = models.TextField()
    sex = models.CharField(max_length=1)


class Examination(models.Model):
    date = models.DateField()
    current_age = models.PositiveSmallIntegerField(blank=True, null=True)
    icd_code = models.CharField(max_length=15, blank=True, null=True)
    json = models.TextField(blank=True, null=True)

    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class KeyWords(models.Model):
    word = models.TextField()


class Description(models.Model):
    name = models.TextField()
    text = models.TextField(blank=True, null=True)

    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    key_words = models.ManyToManyField(KeyWords)


class ImageSeries(models.Model):
    LEFT = 'L'
    RIGHT = 'R'
    EYE_CHOICES = (
        (LEFT, 'Left'),
        (RIGHT, 'Right')
    )
    eye = models.CharField(
        max_length=1,
        choices=EYE_CHOICES,
        blank=True,
        null=True
    )
    name = models.TextField()
    info = models.TextField(blank=True, null=True)

    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)


class ProcessedDescription(models.Model):
    eye = models.CharField(
        max_length=1,
        choices=ImageSeries.EYE_CHOICES,
        blank=True,
        null=True
    )
    text = models.TextField()
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, blank=True, null=True)


class Image(models.Model):
    name = models.TextField()
    image = models.ImageField(
        upload_to="images/",
        height_field="height_field",
        width_field="width_field"
    )
    height_field = models.IntegerField(default=0, null=True)
    width_field = models.IntegerField(default=0, null=True)

    image_series = models.ForeignKey(ImageSeries, on_delete=models.CASCADE)
