from django import forms
from multiupload.fields import MultiFileField, MultiMediaField, MultiImageField

class UploadForm(forms.Form):
    attachments = MultiMediaField(min_num=2, max_num=25, media_type='image')