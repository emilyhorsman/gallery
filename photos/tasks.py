from urllib import request
import shutil

from celery import shared_task


@shared_task
def read_exif_data(uri):
    with request.urlopen(uri) as res, open('foo.jpg', 'wb') as handler:
        shutil.copyfileobj(res, handler)
    import pdb
    pdb.set_trace()
