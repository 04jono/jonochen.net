from django.urls import path
from pages import views

urlpatterns = [
    path("", views.home, name='home'),
    path("resume", views.resume, name='resume'),
    path("playlistle", views.playlistle, name='playlistle'),
    path("song_submit", views.submit_song, name='submit_song'),
]