from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os
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
    

