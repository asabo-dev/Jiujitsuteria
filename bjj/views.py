from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Video, Position, Technique, Guard, Tag
from django.db.models import Count

def index(request):
    context = {
        "positions": Position.objects.all(),
        "techniques": Technique.objects.all(),
        "guards": Guard.objects.all(),
        "tags": Tag.objects.all(),
    }
    return render(request, "bjj/index.html", context)

def category_list(request, category_type):
    model_map = {
        'position': Position,
        'technique': Technique,
        'guard': Guard,
    }
    model = model_map.get(category_type)
    if model:
        categories = model.objects.annotate(video_count=Count('video'))
    else:
        categories = []
    return render(request, 'bjj/category_list.html', {
        'category_type': category_type,
        'categories': categories,
    })

def category_videos(request, category_type, category_id):
    model_map = {
        'position': Position,
        'technique': Technique,
        'guard': Guard,
    }
    model = model_map.get(category_type)
    category = get_object_or_404(model, id=category_id)
    videos = Video.objects.filter(**{category_type: category}).order_by('-id')

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bjj/category_videos.html', {
        'category': category,
        'videos': page_obj,
        'category_type': category_type,
    })

def videos_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    videos = tag.videos.all().order_by('-id')

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bjj/tag_search_results.html', {
        'query': tag.name,
        'tag': tag,
        'videos': page_obj,
    })

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'bjj/video_detail.html', {'video': video})

def tag_search(request):
    query = request.GET.get('q', '').strip().lower()
    tag_terms = query.replace(',', ' ').split()
    videos = Video.objects.all()

    if tag_terms:
        videos = videos.filter(tags__name__in=tag_terms).distinct()

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bjj/tag_search_results.html', {
        'query': query,
        'videos': page_obj,
    })
