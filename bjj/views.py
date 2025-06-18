from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Video, Position, Technique, Guard, Tag

def index(request):
    tags = Tag.objects.all()
    context = {
        "positions": Position.objects.all(),
        "techniques": Technique.objects.all(),
        "guards": Guard.objects.all(),
        "tags": tags,
    }
    return render(request, "bjj/index.html", context)

# Optional: Generic list view of all categories by type
def category_list(request, category_type):
    if category_type == 'position':
        categories = Position.objects.all()
        label = 'Position'
    elif category_type == 'technique':
        categories = Technique.objects.all()
        label = 'Technique'
    elif category_type == 'guard':
        categories = Guard.objects.all()
        label = 'Guard'
    else:
        categories = []
        label = 'Unknown'

    return render(request, 'bjj/category_list.html', {
        'category_type': category_type,
        'categories': categories,
        'label': label,
    })

# Unified view to show videos per category
def category_videos(request, category_type, category_id):
    if category_type == 'position':
        category = get_object_or_404(Position, id=category_id)
        videos = Video.objects.filter(position=category)
    elif category_type == 'technique':
        category = get_object_or_404(Technique, id=category_id)
        videos = Video.objects.filter(technique=category)
    elif category_type == 'guard':
        category = get_object_or_404(Guard, id=category_id)
        videos = Video.objects.filter(guard=category)
    else:
        category = None
        videos = Video.objects.none()

    return render(request, 'bjj/category_videos.html', {
        'category': category,
        'videos': videos,
        'category_type': category_type,
    })

# Optional: Direct views per category (if needed for easy linking)
def videos_by_position(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    videos = Video.objects.filter(position=position)
    return render(request, 'bjj/category_videos.html', {
        'videos': videos,
        'category': position,
        'category_type': 'position',
    })

def videos_by_technique(request, technique_id):
    technique = get_object_or_404(Technique, id=technique_id)
    videos = Video.objects.filter(technique=technique)
    return render(request, 'bjj/category_videos.html', {
        'videos': videos,
        'category': technique,
        'category_type': 'technique',
    })

def videos_by_guard(request, guard_id):
    guard = get_object_or_404(Guard, id=guard_id)
    videos = Video.objects.filter(guard=guard)
    return render(request, 'bjj/category_videos.html', {
        'videos': videos,
        'category': guard,
        'category_type': 'guard',
    })

# ✅ Tag-based video search (works with ManyToManyField)
def tag_search(request):
    query = request.GET.get('q', '').strip().lower()
    tag_terms = query.replace(',', ' ').split()
    videos = Video.objects.all()

    if tag_terms:
        videos = videos.filter(tags__name__in=tag_terms).distinct()

    return render(request, 'bjj/tag_search_results.html', {
        'query': query,
        'videos': videos,
    })

def videos_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    videos = tag.videos.all()
    return render(request, 'bjj/tag_search_results.html', {
        'query': tag.name,
        'videos': videos,
    })
# This code is part of the views.py file for a Django application that handles Brazilian Jiu-Jitsu (BJJ) video content.