from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
# Create your views here.

def playlistle(request):
    return render(request, "playlistle/playlistle.html")

def songofday_modal(request):
    return render(request, "playlistle/songofday_modal.html")

def get_songofday() -> dict:
    '''Get the song of the day'''
    songofday = SongOfDay.objects.latest('date_added').song
    return {"song_name": songofday.song_name, 
            "artist": songofday.artist, 
            "release_year": songofday.release_year, 
            "album_url": songofday.album_url, 
            "playlist": songofday.playlist,
            "song_identifier": songofday.song_identifier}


@csrf_protect
def submit_song(request):
    '''Playlistle form: Submit a song guess'''
    if request.method == 'POST':
        song_string = request.POST.get('song')
        ##if song exists
        req_song = Song.objects.filter(song_identifier=song_string)
        if req_song.exists():
            res = {"exists": True}
            if SongOfDay.objects.latest('date_added').song.song_identifier == str(song_string):
                res["is_song"] = True
            else:
                res["is_song"] = False
            return JsonResponse(res)
        else:
            return JsonResponse({"exists": False})
    else:
        return HttpResponseNotFound("No POST request found")
    

