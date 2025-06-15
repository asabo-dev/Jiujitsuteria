"""Defines URL patterns for bjj."""

from django.urls import path
from . import views

app_name = 'bjj'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:category_type>/<int:category_id>/', views.category_videos, name='category_videos'),
    path('tags/', views.tag_search, name='tag_search'),
]
# The above code defines URL patterns for the Brazilian Jiu-Jitsu (BJJ) application.
# It includes paths for the index view, category-specific video listings, and tag search functionality.
# The `app_name` variable is set to 'bjj' to namespace the URLs, allowing for easier reference in templates and views.
