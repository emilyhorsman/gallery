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
    photo_file.photo.exif = exif
    photo_file.photo.save()
    photo_file.save()
    return path


@shared_task
def resize(source, name, extension, width, photo_file_pk):
    _, target = tempfile.mkstemp()
    source_photo_file = PhotoFile.objects.get(pk=photo_file_pk)
    with Image(filename=source) as image:
        # No cropping.
        # Resize to width while preserving aspect ratio by not
        # specifying height.
        image.transform('', str(width))
        image.save(filename=target)

        photo_file = PhotoFile(
            photo=source_photo_file.photo,
            format=image.format,
            is_original=False,
            processor='resize task {}'.format(width),
        )
    target_name = source_photo_file.file.storage.get_available_name(name + extension)
    with open(target, 'rb') as handler:
        photo_file.file.save(
            target_name,
            File(handler),
            save=True,
        )


def convert_image(target, name, photo_file_pk, **kwargs):
    source_photo_file = PhotoFile.objects.get(pk=photo_file_pk)
    subprocess.run(kwargs['params'])

    photo_file = PhotoFile(
        photo=source_photo_file.photo,
        format=kwargs['format'],
        is_original=False,
        processor=' '.join(kwargs['params']),
    )
    # We want to retain the uploaded filename instead of an entirely randomly
    # generated one.
    target_name = source_photo_file.file.storage.get_available_name(name + kwargs['extension'])
    with open(target, 'rb') as handler:
        photo_file.file.save(
            target_name,
            File(handler),
            save=True,
        )


@shared_task
def convert_to_webp(source, name, photo_file_pk):
    _, target = tempfile.mkstemp()
    params = (
        'cwebp',
        '-hint', 'photo',
        '-q', '75',
        '-m', '6',
        '-mt',
        '-af',
        source,
        '-o', target,
    )
    convert_image(
        target,
        name,
        photo_file_pk,
        params=params,
        format='WEBP',
        extension='.webp',
    )
    return target


@shared_task
def convert_with_mozjpeg(source, name, photo_file_pk):
    _, target = tempfile.mkstemp()
    params = (
        'mozcjpeg',
        '-outfile', target,
        '-q', '75',
        source,
    )
    convert_image(
        target,
        name,
        photo_file_pk,
        params=params,
        format='JPEG',
        extension='.jpg',
    )
    return target


@shared_task
def convert_to_guetzli(source, name, photo_file_pk):
    _, target = tempfile.mkstemp()
    params = (
        'guetzli',
        '--quality', '84',
        source,
        target,
    )
    convert_image(
        target,
        name,
        photo_file_pk,
        params=params,
        format='JPEG',
        extension='.jpg',
    )
    return target
