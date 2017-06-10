from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


class PhotoFile(models.Model):
    PHOTO_FILE_DIR = 'photos/'

    photo = models.ForeignKey(
        'photos.Photo',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    file = models.ImageField(upload_to=PHOTO_FILE_DIR)
    is_original = models.BooleanField(default=True)
    format = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )
    exif = JSONField(null=True, blank=True)

    def __str__(self):
        return '{} for {}'.format(self.format, self.photo)


class Photo(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
