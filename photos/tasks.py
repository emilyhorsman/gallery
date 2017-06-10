import tempfile
from urllib import request
import shutil
import subprocess

from celery import shared_task
from django.core.files import File
from wand.image import Image

from photos.models import PhotoFile


@shared_task
def download_image(photo_file_pk, url):
    _, path = tempfile.mkstemp()
    with request.urlopen(url) as res, open(path, 'wb') as handler:
        shutil.copyfileobj(res, handler)
    return path


@shared_task
def read_metadata(path, photo_file_pk):
    photo_file = PhotoFile.objects.get(pk=photo_file_pk)
    exif = dict()
    with Image(filename=path) as image:
        photo_file.format = image.format
        for key, value in image.metadata.items():
            exif[key] = value
    photo_file.exif = exif
    photo_file.save()
    return path


@shared_task
def convert_to_webp(source, name, photo_file_pk):
    source_photo_file = PhotoFile.objects.get(pk=photo_file_pk)
    _, target = tempfile.mkstemp()
    params = (
        'cwebp',
        '-hint', 'photo',
        '-q', '60',
        source,
        '-o', target,
    )
    subprocess.run(params)

    photo_file = PhotoFile(
        photo=source_photo_file.photo,
        format='WEBP',
        is_original=False,
    )
    # We want to retain the uploaded filename instead of an entirely randomly
    # generated one.
    target_name = source_photo_file.file.storage.get_available_name(name + '.webp')
    with open(target, 'rb') as handler:
        photo_file.file.save(
            target_name,
            File(handler),
            save=True,
        )
    return source
