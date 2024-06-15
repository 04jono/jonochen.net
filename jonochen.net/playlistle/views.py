from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponseServerError, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
import ffmpeg
import string
import datetime

# Create your views here.

def playlistle(request):
    date = request.GET.get('date', None)
    if date != None:
        try: 
            return render(request, "playlistle/playlistle.html", get_songofday(date))
        except ValueError:
            return HttpResponse("There was an problem with your request", 400)
    else:
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

def get_songofday(date : str | None = None) -> dict:
    '''Get the song of the day. Optional: specify date string'''
    
    if date == None:
        songofday = SongOfDay.objects.latest('date_added')
        curr_song = songofday.song
        return {"song_name": curr_song.song_name, 
            "artist": curr_song.artist, 
            "release_year": curr_song.release_year, 
            "album_url": curr_song.album_url, 
            "playlist": curr_song.playlist,
            "song_identifier": curr_song.song_identifier,
            "date_added": songofday.date_added.strftime("%Y-%m-%d")
            }
    else:
        date_format = "%Y-%m-%d"
        parsed_date = datetime.datetime.strptime(date, date_format).date()
        songofday = SongOfDay.objects.filter(date_added=parsed_date).first()
        curr_song = songofday.song
        return {"song_name": curr_song.song_name, 
            "artist": curr_song.artist, 
            "release_year": curr_song.release_year, 
            "album_url": curr_song.album_url, 
            "playlist": curr_song.playlist,
            "song_identifier": curr_song.song_identifier,
            "date_added": songofday.date_added.strftime("%Y-%m-%d")
        }
        
        


@csrf_protect
def submit_song(request):
    '''Playlistle form: Submit a song guess'''
    if request.method == 'POST':
        song_string = request.POST.get('song')
        ##if song exists
        req_song = Song.objects.filter(song_identifier=song_string)
        if req_song.exists():
            res = {"exists": True}
            
            date = request.GET.get('date', None)
            songofday = SongOfDay.objects.latest('date_added').song
            if date != None:
                try:
                    date_format = "%Y-%m-%d"
                    parsed_date = datetime.datetime.strptime(date, date_format).date()
                    songofday = SongOfDay.objects.filter(date_added=parsed_date).first().song
                except:
                    songofday = SongOfDay.objects.latest('date_added').song
        
            if songofday.song_identifier == str(song_string):
                res["is_song"] = True
            else:
                if songofday.artist == str(song_string).split(" - ")[0].translate(str.maketrans('', '', string.punctuation)):
                    #Same artist
                    res["is_artist"] = True
                else:
                    res["is_artist"] = False
                res["is_song"] = False
            return JsonResponse(res)
        else:
            return JsonResponse({"exists": False})
    else:
        return HttpResponseNotFound("No POST request found")
    

