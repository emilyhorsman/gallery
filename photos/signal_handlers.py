import os
from urllib.parse import urljoin

from celery import chain
from django.dispatch import receiver
from django.db.models.signals import post_save

from photos.models import PhotoFile
from photos.tasks import download_image, read_metadata, convert_to_webp


@receiver(post_save, sender=PhotoFile)
def post_save_process_image(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.is_original:
        return

    url = os.environ.get('BASE_URL', '')
    name, _ = os.path.splitext(os.path.basename(instance.file.name))
    chain(
        download_image.s(
            instance.pk,
            urljoin(url, instance.file.url),
        ),

        read_metadata.s(instance.pk),
        convert_to_webp.s(name, instance.pk),
    )()
