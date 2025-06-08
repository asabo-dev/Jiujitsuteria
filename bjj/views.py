from django.shortcuts import render
from .models import Video, Position, Technique, Guard

def index(request):
    positions = Position.objects.all()
    techniques = Technique.objects.all()
    guards = Guard.objects.all()

    print("INDEX VIEW LOADED")  # Confirm this shows in your terminal

    context = {
        'positions': positions,
        'techniques': techniques,
        'guards': guards,
    }
    return render(request, 'bjj/index.html', context)
    
def video_search(request):
    """Filter videos list for display."""
    positions = Position.objects.all()
    techniques = Technique.objects.all()
    guards = Guard.objects.all()

    videos = Video.objects.all()

    # Apply filters if parameters are present in the request
    position = request.GET.get('position')
    technique = request.GET.get('technique')
    guard = request.GET.get('guard')

    if position:
        videos = videos.filter(position__name=position)
    if technique:
        videos = videos.filter(technique__name=technique)
    if guard:
        videos = videos.filter(guard__name=guard)

    context = {
        'positions': positions,
        'techniques': techniques,
        'guards': guards,
        'videos': videos,
    }
    
    return render(request, 'bjj/video_search.html', context)
