from django.urls import path
from playlistle import views

urlpatterns = [
    path("", views.playlistle, name='playlistle'),
    path("song_submit", views.submit_song, name='submit_song'),
]