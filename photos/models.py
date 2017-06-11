import operator

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


def has_webp_support(user_agent):
    return user_agent['family'] == 'Chrome'


class PhotoFile(models.Model):
    PHOTO_FILE_DIR = 'photos/'
    USER_UPLOAD_PROCESSOR = 'USER_UPLOAD'

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
    processor = models.CharField(
        max_length=2048,
        default=USER_UPLOAD_PROCESSOR,
    )

    def __str__(self):
        return '{}{} for {} ({}x{})'.format(
            'Original ' if self.is_original else '',
            self.format,
            self.photo,
            self.file.width,
            self.file.height,
        )


class Photo(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        null=True,
    )
    published = models.BooleanField(default=False)
    exif = JSONField(null=True, blank=True)

    def get_srcset(self, user_agent):
        qs = self.photos.filter(is_original=False)
        if not has_webp_support(user_agent):
            qs = qs.exclude(format='WEBP')

        photo_files = sorted(
            qs,
            key=operator.attrgetter('file.size'),
        )

        srcset = [
            '{} {}w'.format(photo.file.url, photo.file.width)
            for photo in photo_files
        ]
        return ', '.join(srcset)

    def __str__(self):
        return self.title
