from django.db import models

from data_module.models import Person

# Create your models here.


class Patient(models.Model):
    GENDER_CHOICES = (('M', 'Male',), ('F', 'Female',))

    model_name = 'patient'
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=False, null=False)
    sex = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=False, default='M')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        person = Person(sex=self.sex)
        person.save()

        self.person = person
        
        super(Patient, self).save(*args, **kwargs)
