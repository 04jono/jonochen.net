from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.views.decorators.http import require_GET
import os
# Create your views here.

ROBOTS_TXT = """\
User-Agent: *
Disallow: /resume
Disallow: /admin
Disallow: /playlistle

User-agent: GPTBot
Disallow: /
"""

ALLOW_RESUME = False

@require_GET
def robots(request):
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")

def home(request):
    return render(request, "pages/home.html")

def resume(request):
    if not ALLOW_RESUME:
        return HttpResponseForbidden("Resume disabled")
    
    file_path = os.path.join(settings.BASE_DIR, 'pages/files/resume/resume.pdf')

    # Open the PDF file in binary mode
    if os.path.exists(file_path):
        pdf_file = open(file_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="resume.pdf"'
        return response
    else:
        return HttpResponseNotFound("No Resume file found")
    

