from django.urls import path
from pages import views

urlpatterns = [
    path("", views.home, name='home'),
    path("about", views.about, name='about'),
    path("projects", views.projects, name='projects'),
    path("robots.txt", views.robots, name='robots'),
    path("resume", views.resume, name='resume'),
]