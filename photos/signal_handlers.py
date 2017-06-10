import os
from urllib.parse import urljoin

from django.dispatch import receiver
from django.db.models.signals import post_save

from photos.models import PhotoFile
from photos.tasks import read_exif_data


@receiver(post_save, sender=PhotoFile)
def post_save_read_exif_data(sender, instance, created, **kwargs):
    if not created:
        return

    url = os.environ.get('BASE_URL', '')
    read_exif_data.delay(
        instance.pk,
        urljoin(url, instance.file.url)
    )


