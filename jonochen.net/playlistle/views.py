from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
import ffmpeg
# Create your views here.

def playlistle(request):
    return render(request, "playlistle/playlistle.html")

@csrf_protect
def get_clipped_song(request):
    '''Get the song of the day, clipped to length [0, 30] seconds'''
    if request.method == 'GET':
        songofday = SongOfDay.objects.latest('date_added').song
        input_file = os.path.join(settings.MEDIA_ROOT, songofday.database_uri)
        length = int(request.GET.get('length'))
        out, err = ffmpeg.input(input_file, t=length).output("pipe:").run(capture_stdout=True)
        return FileResponse(out, content_type='audio/mp3')
    else:
        return HttpResponseNotFound("No GET request found")
    
def songofday_modal(request):
    return render(request, "playlistle/songofday_modal.html")

@csrf_protect
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
    

