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

def category_videos(request, category_type, category_id):
    model_map = {
        "position": Position,
        "technique": Technique,
        "guard": Guard
    }
    model = model_map.get(category_type)
    if not model:
        return render(request, "bjj/error.html", {"message": "Invalid category."})

    category = get_object_or_404(model, pk=category_id)
    videos = Video.objects.filter(**{f"{category_type}": category})
    
    return render(request, "bjj/category_videos.html", {
        "category_type": category_type,
        "category": category,
        "videos": videos,
    })

def tag_search(request):
    query = request.GET.get("q")
    videos = Video.objects.filter(tags__name__icontains=query).distinct()
    return render(request, "bjj/tag_search_results.html", {
        "query": query,
        "videos": videos
    })
