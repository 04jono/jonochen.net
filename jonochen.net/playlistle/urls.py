from django.urls import path
from playlistle import views

urlpatterns = [
    path("", views.playlistle, name='playlistle'),
    path("song_submit", views.submit_song, name='submit_song'),
    path("song_clip", views.get_clipped_song, name='get_clipped_song'),
    path("songofday_modal", views.songofday_modal, name='songofday_modal')
]