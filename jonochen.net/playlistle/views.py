from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
# Create your views here.

def playlistle(request):
    return render(request, "playlistle/playlistle.html")

@csrf_protect
def submit_song(request):
    '''Playlistle form: Submit a song guess'''
    if request.method == 'POST':
        song_string = request.POST.get('song')
        ##if song exists
        req_song = Song.objects.filter(pk=song_string)
        if req_song.exists():
            res = {"exists": True}
            is_song = SongOfDay.objects.latest('date_added').song.filter(pk=song_string)
            if is_song.exists():
                res["is_song"] = True
            else:
                res["is_song"] = False
            return JsonResponse(res)
        else:
            return JsonResponse({"exists": False})
    else:
        return HttpResponseNotFound("No POST request found")
    

