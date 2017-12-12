from django.db import models

# Create your models here.

class Person(models.Model):
    GENDER_CHOICES = (('M', 'Male',), ('F', 'Female',))

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    code_name = models.TextField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


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
    name = models.TextField(blank=True, null=True)
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
    order = models.IntegerField(blank=True, null=True)

    image_series = models.ForeignKey(ImageSeries, on_delete=models.CASCADE, null=True)
