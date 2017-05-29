from django.contrib import admin

from .models import Photo, PhotoFile


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(PhotoFile)
class PhotoFileAdmin(admin.ModelAdmin):
    pass
