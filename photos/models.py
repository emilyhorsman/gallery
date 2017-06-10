import os
from urllib.parse import urljoin

from django.conf import settings
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save

from photos.tasks import read_exif_data


class PhotoFile(models.Model):
    PHOTO_FILE_DIR = 'photos/'

    FORMAT_CHOICES = [
        ('JPEG', 'JPEG'),
        ('WEBP', 'WebP'),
    ]

    EXTENSION_TO_FORMAT_CHOICE = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.webp': 'WEBP',
    }

    photo = models.ForeignKey(
        'photos.Photo',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    file = models.ImageField(upload_to=PHOTO_FILE_DIR)
    is_original = models.BooleanField(default=True)
    format = models.CharField(
        max_length=max([len(choice[0]) for choice in FORMAT_CHOICES]),
        choices=FORMAT_CHOICES,
    )

    def __str__(self):
        return '{} for {}'.format(self.format, self.photo)


@receiver(post_save, sender=PhotoFile)
def post_save_read_exif_data(sender, instance, **kwargs):
    url = os.environ.get(BASE_URL, '')
    read_exif_data.delay(urljoin(url, instance.file.url))



class Photo(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    published = models.BooleanField(default=False)
    base_name = models.CharField(max_length=4096, unique=True)

    def __str__(self):
        return '{} ({})'.format(self.title, self.base_name)
