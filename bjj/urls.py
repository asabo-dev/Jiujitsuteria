"""Defines URL patterns for bjj."""

from django.urls import path

from . import views

app_name = 'bjj'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    # Page that shows all videos.
    path('videos/', views.video_search, name='videos'),
    # path('positions/', views.positions, name='positions'),  # <- Commented out, view not implemented yet
]
