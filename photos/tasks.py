import urllib

from celery import shared_task


@shared_task
def read_exif_data(uri):
    image = urllib.URLopener()
    result = image.retrieve(uri, 'foo.jpg')
    import pdb
    pdb.set_trace()
