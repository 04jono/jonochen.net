from django.urls import path
from playlistle import views

urlpatterns = [
    path("", views.playlistle, name='playlistle'),
    path("song_submit", views.submit_song, name='submit_song'),
    path("song_clip", views.get_clipped_song, name='get_clipped_song'),
    path("song_hash", views.get_song_hash, name='get_song_hash'),
    path("song_identifiers", views.get_all_song_identifiers, name='get_all_song_identifiers'),
]