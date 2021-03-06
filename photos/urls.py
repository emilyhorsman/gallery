from django.conf.urls import url

from photos.views import (
    PhotoDetailView,
    PhotoCreateView,
)


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photo-detail'),
    url(r'^create/$', PhotoCreateView.as_view(), name='photo-create'),
]
