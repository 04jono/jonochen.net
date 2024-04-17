from django.contrib import admin

# Register your models here.

from .models import Song, SongOfDay

admin.site.register(Song)
admin.site.register(SongOfDay)
