from django.db import models

from data_module import models as dataModels

# Create your models here.


class Patient(models.Model):
    GENDER_CHOICES = (('M', 'Male',), ('F', 'Female',))

    model_name = 'patient'
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=False, null=False)
    sex = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=False, default='M')

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        super(Patient, self).save(*args, **kwargs)

        person = dataModels.Person(sex=self.sex, patient=self)
        person.save()
