from __future__ import unicode_literals

from django import forms
from multiupload.fields import MultiMediaField

from data_module.models import Examination, Description, Person


class PatientForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'code_name',
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
            'date'
        ]

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
            })
        }


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Description
        fields = [
            'text'
        ]
        labels = {
            'text': 'Comment',
        }


class UploadForm(forms.Form):
    attachments = MultiMediaField(label='Images', min_num=2, max_num=16, media_type='image')


class CombinedFormBase(forms.Form):
    form_classes = []

    def __init__(self, *args, **kwargs):
        super(CombinedFormBase, self).__init__(*args, **kwargs)
        for f in self.form_classes:
            name = f.__name__.lower()
            setattr(self, name, f(*args, **kwargs))
            form = getattr(self, name)
            self.fields.update(form.fields)
            self.initial.update(form.initial)

    def is_valid(self):
        isValid = True
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            if not form.is_valid():
                isValid = False
        # is_valid will trigger clean method
        # so it should be called after all other forms is_valid are called
        # otherwise clean_data will be empty
        if not super(CombinedFormBase, self).is_valid():
            isValid = False
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            self.errors.update(form.errors)
        return isValid

    def clean(self):
        cleaned_data = super(CombinedFormBase, self).clean()
        for f in self.form_classes:
            name = f.__name__.lower()
            form = getattr(self, name)
            cleaned_data.update(form.cleaned_data)
        return cleaned_data


class ExaminationCombinedForm(CombinedFormBase):
    form_classes = [ExaminationForm, DescriptionForm, UploadForm]
