from django.shortcuts import render, get_object_or_404
from .models import Video, Position, Technique, Guard, Tag
from django.db.models import Q

def index(request):
    tags = Tag.objects.all()
    context = {
        "positions": Position.objects.all(),
        "techniques": Technique.objects.all(),
        "guards": Guard.objects.all(),
        "tags": tags,
    }
    return render(request, "bjj/index.html", context)

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


def tag_search(request):
    query = request.GET.get('q', '').strip().lower()
    tags = query.replace(',', ' ').split()
    videos = Video.objects.all()

    for tag in tags:
        videos = videos.filter(tags__icontains=tag)

    return render(request, 'bjj/tag_search_results.html', {
        'query': query,
        'videos': videos,
    })
