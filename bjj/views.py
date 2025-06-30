from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Video, Position, Technique, Guard, Tag
from django.db.models import Count

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
        categories = Position.objects.annotate(video_count=Count('video'))
        label = 'Position'
    elif category_type == 'technique':
        categories = Technique.objects.annotate(video_count=Count('video'))
        label = 'Technique'
    elif category_type == 'guard':
        categories = Guard.objects.annotate(video_count=Count('video'))
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
        videos = Video.objects.filter(position=category).order_by('-id')
    elif category_type == 'technique':
        category = get_object_or_404(Technique, id=category_id)
        videos = Video.objects.filter(technique=category).order_by('-id')
    elif category_type == 'guard':
        category = get_object_or_404(Guard, id=category_id)
        videos = Video.objects.filter(guard=category).order_by('-id')
    else:
        category = None
        videos = Video.objects.none()

    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bjj/category_videos.html', {
        'category': category,
        'videos': page_obj,
        'category_type': category_type,
    })

# Optional direct views
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

def tag_search(request):
    query = request.GET.get('q', '').strip().lower()
    tag_terms = query.replace(',', ' ').split()
    videos = Video.objects.all()

    if tag_terms:
        videos = videos.filter(tags__name__in=tag_terms).distinct()

    paginator = Paginator(videos, 12)  # 12 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bjj/tag_search_results.html', {
        'query': query,
        'videos': page_obj,
    })

def videos_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    videos = tag.videos.all().order_by('-id')  # Optional: newest first

    paginator = Paginator(videos, 12)  # 12 videos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bjj/tag_search_results.html', {
        'query': tag.name,
        'tag': tag,
        'videos': page_obj,
    })
