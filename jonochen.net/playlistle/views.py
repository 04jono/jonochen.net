from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponseServerError, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
import ffmpeg
# Create your views here.

def playlistle(request):
    return render(request, "playlistle/playlistle.html", get_songofday())

@csrf_protect
def get_all_song_identifiers(request):
    '''Get all song identifiers'''
    if request.method == 'GET':
        song_identifiers = [song.song_identifier for song in Song.objects.all()]
        return JsonResponse({"song_identifiers": song_identifiers})
    else:
        return HttpResponseNotFound("No GET request found")

@csrf_protect
def get_song_hash(request):
    '''Get the song of the day hash'''
    if request.method == 'GET':
        songofday = SongOfDay.objects.latest('date_added').song
        return JsonResponse({"song_hash": hash(songofday.song_identifier)})
    else:
        return HttpResponseNotFound("No GET request found")

@csrf_protect
def get_clipped_song(request):
    '''Get the song of the day, clipped to length [0, 30] seconds'''
    if request.method == 'GET':
        try:
            songofday = SongOfDay.objects.latest('date_added').song
            input_file = os.path.join(settings.MEDIA_ROOT, songofday.database_uri)
            length = int(request.GET.get('length'))
            out, err = ffmpeg.input(input_file, t=length).output("pipe:", format="mp3").run(capture_stdout=True)

            response = HttpResponse()
            response.write(out)
            response['Content-Type'] ='audio/mp3'
            response['Content-Length'] = len(out)
            return response
        except Exception as e:
            print(e)
            return HttpResponseServerError("Error processing song")
    else:
        return HttpResponseNotFound("No GET request found")

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
    

