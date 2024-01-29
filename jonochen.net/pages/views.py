from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
from .models import Song, SongOfDay
# Create your views here.


def home(request):
    return render(request, "pages/home.html")

def resume(request):
    file_path = os.path.join(settings.BASE_DIR, 'pages/files/resume/resume.pdf')

    # Open the PDF file in binary mode
    if os.path.exists(file_path):
        pdf_file = open(file_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="resume.pdf"'
        return response
    else:
        return HttpResponseNotFound("No Resume file found")

def playlistle(request):
    return render(request, "pages/playlistle.html")

@csrf_protect
def submit_song(request):
    '''Playlistle form: Submit a song guess'''
    if request.method == 'POST':
        song_string = request.POST.get('song')
        ##if song exists
        req_song = Song.objects.filter(pk=song_string)
        if req_song.exists():
            res = {"exists": True}
            is_song = SongOfDay.objects.filter(song=req_song)
            if is_song.exists():
                res["is_song"] = True
            else:
                res["is_song"] = False
            return JsonResponse(res)
        else:
            return JsonResponse({"exists": False})
    else:
        return HttpResponseNotFound("No POST request found")
    

