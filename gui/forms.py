from __future__ import unicode_literals

from django import forms

from gui import models


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
                'class': 'datepicker-input',
                'data-target': '#datetimepicker_date',
            }),
        }
