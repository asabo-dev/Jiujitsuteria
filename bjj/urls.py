"""Defines URL patterns for bjj."""

from django.urls import path
from . import views

app_name = 'bjj'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:category_type>/', views.category_list, name='category_list'),
    path('category/<str:category_type>/<int:category_id>/', views.category_videos, name='category_videos'),
    path('search/', views.tag_search, name='tag_search'),
    
]
# The above code defines URL patterns for the BJJ app, including the index page,
# category listing, category-specific video listings, and tag search functionality.
# It uses Django's path function to map URLs to views in the views.py file.