import os
from urllib.parse import urljoin

from celery import chain
from django.dispatch import receiver
from django.db.models.signals import post_save

from photos.models import PhotoFile
from photos.tasks import download_image, read_exif_data


@receiver(post_save, sender=PhotoFile)
def post_save_process_image(sender, instance, created, **kwargs):
    if not created:
        return

    url = os.environ.get('BASE_URL', '')
    chain(
        download_image.s(
            instance.pk,
            urljoin(url, instance.file.url),
        ),

        read_exif_data.s(instance.pk),
    )()
