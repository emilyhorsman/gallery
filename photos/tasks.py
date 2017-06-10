import tempfile
from urllib import request
import shutil

from celery import shared_task


@shared_task
def read_exif_data(uri):
    _, path = tempfile.mkstemp()
    with request.urlopen(uri) as res, open(path, 'wb') as handler:
        shutil.copyfileobj(res, handler)
