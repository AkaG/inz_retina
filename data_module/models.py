from django.db import models


# Create your models here.

class Person(models.Model):
    code_name = models.TextField()
    sex = models.CharField(max_length=1)


class Examination(models.Model):
    date = models.DateField()
    current_age = models.PositiveSmallIntegerField()
    icd_code = models.CharField(max_length=15)

    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class KeyWords(models.Model):
    word = models.TextField()


class Description(models.Model):
    text = models.TextField()

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
        choices=EYE_CHOICES
    )

    info = models.TextField()

    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)


class Image(models.Model):
    image = models.ImageField(
        upload_to="images/",
        height_field="height_field",
        width_field="width_field"
    )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    image_series = models.ForeignKey(ImageSeries, on_delete=models.CASCADE)
