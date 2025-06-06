from django.shortcuts import render
from .models import Video, Position, Technique, Guard

def index(request):
    context = {
        'positions': Position.objects.all(),
        'techniques': Technique.objects.all(),
        'guards': Guard.objects.all(),
    }
    return render(request, 'bjj/index.html', context)

def video_search(request):
    position = request.GET.get('position')
    technique = request.GET.get('technique')
    guard = request.GET.get('guard')

    videos = Video.objects.all()

    if position:
        videos = videos.filter(position__name__icontains=position)
    if technique:
        videos = videos.filter(technique__name__icontains=technique)
    if guard:
        videos = videos.filter(guard__name__icontains=guard)

    return render(request, 'bjj/search_results.html', {'videos': videos})
