import tempfile
from urllib import request
import shutil

from celery import shared_task
from wand.image import Image

from photos.models import PhotoFile


@shared_task
def download_image(photo_file_pk, url):
    _, path = tempfile.mkstemp()
    with request.urlopen(url) as res, open(path, 'wb') as handler:
        shutil.copyfileobj(res, handler)
    return path


@shared_task
def read_exif_data(path, photo_file_pk):
    exif = dict()
    with Image(filename=path) as image:
        for key, value in image.metadata.items():
            exif[key] = value
    photo_file = PhotoFile.objects.get(pk=photo_file_pk)
    photo_file.exif = exif
    photo_file.save()
    return path
