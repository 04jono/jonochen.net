from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Song(models.Model):
    song_name = models.CharField('Song Name', max_length=255)
    artist = models.CharField('Artist', max_length=255)
    release_year = models.CharField('Release Year', max_length=255)
    album_url = models.CharField('Album URL', max_length=255)
    database_uri = models.CharField('Database URI', primary_key=True, max_length=255)

    def __str__(self):
        return self.song_name + " - " + self.artist
    
class SongOfDay(models.Model):
    date_added = models.DateField('Date Added', auto_now_add=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)