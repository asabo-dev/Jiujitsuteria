"""Defines URL patterns for bjj."""

from django.urls import path
from . import views

app_name = 'bjj'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Category listings and videos
    path('category/<str:category_type>/', views.category_list, name='category_list'),
    path('category/<str:category_type>/<int:category_id>/', views.category_videos, name='category_videos'),
    
    # Tag search via form
    path('search/', views.tag_search, name='tag_search'),

    # (Optional) Browse by specific tag
    path('tag/<int:tag_id>/', views.videos_by_tag, name='videos_by_tag'),
]
