"""Defines URL patterns for bjj."""

from django.urls import path

from . import views

app_name = 'bjj'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
]