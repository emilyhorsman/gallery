from django.conf.urls import url

from photos.views import PhotoDetailView


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photo-detail'),
]
