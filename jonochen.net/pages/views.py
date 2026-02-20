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
Disallow: /about
Disallow: /projects
Disallow: /blog

User-agent: GPTBot
Disallow: /
"""

ALLOW_RESUME = True

@require_GET
def robots(request):
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")

def render_page(request, partial, current_page):
    ctx = {"partial": partial, "current_page": current_page}
    if request.headers.get('HX-Request'):
        return render(request, partial, ctx)
    return render(request, "pages/base.html", ctx)

def home(request):
    return render_page(request, "pages/home.html", "home")

def about(request):
    return render_page(request, "pages/about.html", "about")

def projects(request):
    return render_page(request, "pages/projects.html", "projects")

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
    

