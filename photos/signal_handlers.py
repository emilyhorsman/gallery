import os
from urllib.parse import urljoin

from celery import chain, group
from django.dispatch import receiver
from django.db.models.signals import post_save

from photos.models import PhotoFile
from photos import tasks


WIDTHS = [
    2560,
    1920,
    1536,
    1280,
    1024,
]


@receiver(post_save, sender=PhotoFile)
def post_save_process_image(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.is_original:
        return

    url = os.environ.get('BASE_URL', '')
    name, _ = os.path.splitext(os.path.basename(instance.file.name))
    chain(
        tasks.download_image.s(
            instance.pk,
            urljoin(url, instance.file.url),
        ),

        tasks.read_metadata.s(instance.pk),
        group(
            # Links here are written manually since the result of the
            # penultimate task was not applying to each sub-chain in a
            # group.
            tasks.convert_to_webp.s(
                name,
                instance.pk
            ).set(link=group(
                tasks.resize.s(name, '.webp', width, instance.pk)
                for width in WIDTHS
            )),

            tasks.convert_with_mozjpeg.s(
                name,
                instance.pk,
            ).set(link=group(
                tasks.resize.s(name, '.jpg', width, instance.pk)
                for width in WIDTHS
            )),
        )
    )()
