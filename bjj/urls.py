from django.urls import path
from . import views

app_name = 'bjj'

urlpatterns = [
    path('', views.index, name='index'),

    # Category views
    path('category/<str:category_type>/', views.category_list, name='category_list'),
    path('category/<str:category_type>/<int:category_id>/', views.category_videos, name='category_videos'),

    # Tag search and views
    path('search/', views.tag_search, name='tag_search'),
    path('tag/<int:tag_id>/', views.videos_by_tag, name='videos_by_tag'),

    # Video detail
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
]
