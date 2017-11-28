from __future__ import unicode_literals

from django import forms

from gui import models
from data_module.models import Examination


class PatientForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = [
            'first_name',
            'last_name',
            'birth_date',
            'sex'
        ]

        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
            }),
            'sex': forms.RadioSelect()
        }


class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = [
            'person',
            'json',
            'date'
        ]

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
            })
        }
