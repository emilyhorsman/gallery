import os

from django.core.files import File, storage
from django.core.management.base import BaseCommand
from django.db import transaction

from photos.models import Photo, PhotoFile


storage_kls = storage.get_storage_class()


VALID_IMAGE_EXTENSIONS = ['.jpg', '.webp']


def get_photos(path):
    """Produces a dictionary from the files in a storage directory at a path.
    The files are split into their base and extension and a dictionary is
    returned where the keys are bases and values are a list of extensions.

    A directory of test.jpg and test.webp would return
    { 'test': ['.jpg', '.webp'] }

    Pairs such as test.jpg and test.jpg.webp are not currently supported.
    """
    storage = storage_kls()
    files = dict()
    for file in storage.listdir(path)[1]:
        base, ext = os.path.splitext(file)
        if ext not in VALID_IMAGE_EXTENSIONS:
            continue

        if base not in files:
            files[base] = []
        files[base].append(ext)
    return files


@transaction.atomic
def create_photo(base, sub_path, extensions):
    photo, _ = Photo.objects.get_or_create(published=False, base_name=base)
    storage = storage_kls()
    location = storage.location
    to_delete = []
    for ext in extensions:
        path = os.path.join(location, sub_path, base + ext)
        photo_file = PhotoFile(
            photo=photo,
            format=PhotoFile.EXTENSION_TO_FORMAT_CHOICE[ext.lower()],
            is_original=False,
        )
        handler = open(path, 'rb')
        photo_file.file.save(base + ext, File(handler), save=True)
        to_delete.append(os.path.join(sub_path, base + ext))

    # Only delete things if we haven't bailed by now.
    for path in to_delete:
        storage.delete(path)


class Command(BaseCommand):
    help = 'Imports photos found in the media directory'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        path = options['path']
        for base, extensions in get_photos(path).items():
            create_photo(base, path, extensions)
