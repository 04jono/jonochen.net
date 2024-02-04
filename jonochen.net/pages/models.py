from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Song(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.CharField(max_length=255)
    album_url = models.CharField(max_length=255)
    spotify_uri = models.CharField(primary_key=True, max_length=255)

    def __str__(self):
        return self.name + " - " + self.artist
    
class SongOfDay(models.Model):
    date = models.DateField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)