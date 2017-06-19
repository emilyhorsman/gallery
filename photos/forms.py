from django.db import models
from django.forms import Form, ModelForm, FileField

from photos.models import Photo


class PhotoForm(ModelForm):
    file = FileField()

    class Meta:
        model = Photo
        fields = ['title', 'file']
