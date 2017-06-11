from django.db import models
from django.forms import ModelForm, FileField

from photos.models import Photo, PhotoFile


class PhotoForm(ModelForm):
    file = FileField()

    class Meta:
        model = Photo
        fields = ['title', 'file']

