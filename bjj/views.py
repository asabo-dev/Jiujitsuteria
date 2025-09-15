"""Views for Brazilian Jiu-Jitsu (BJJ) video management and display.
Includes video upload, listing, categorization, and searching by tags."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count

from .forms import VideoUploadForm
from .models import Video, Position, Technique, Guard, Tag


# Reusable map for category models
MODEL_MAP = {
    'position': Position,
    'technique': Technique,
    'guard': Guard,
}


def staff_check(user):
    return user.is_staff


@login_required
@user_passes_test(staff_check)
def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            # video.uploader = request.user   # Uncomment if uploader field exists
            video.save()
            # Redirect to homepage OR video detail page
            # return redirect('bjj:index')
            return redirect('bjj:video_detail', video_id=video.id)
    else:
        form = VideoUploadForm()
    return render(request, 'bjj/upload_video.html', {'form': form})


def index(request):
    context = {
        "positions": Position.objects.all(),
        "techniques": Technique.objects.all(),
        "guards": Guard.objects.all(),
        "tags": Tag.objects.all(),
    }
    return render(request, "bjj/index.html", context)


def category_list(request, category_type):
    model = MODEL_MAP.get(category_type)
    categories = (
        model.objects.annotate(video_count=Count('video')).order_by('name')
        if model else []
    )
    return render(request, 'bjj/category_list.html', {
        'category_type': category_type,
        'categories': categories,
    })


def category_videos(request, category_type, category_id):
    model = MODEL_MAP.get(category_type)
    category = get_object_or_404(model, id=category_id)
    videos = Video.objects.filter(**{category_type: category}).order_by('-id')

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bjj/category_videos.html', {
        'category': category,
        'videos': page_obj,
        'category_type': category_type,
        'video_count': videos.count(),  # ✅ total count
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
        'video_count': videos.count(),  # ✅ total count
    })


def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    return render(request, 'bjj/video_detail.html', {'video': video})


def tag_search(request):
    query = request.GET.get('q', '').strip().lower()
    tag_terms = [term.strip() for term in query.replace(',', ' ').split() if term.strip()]

    videos = Video.objects.all()
    for term in tag_terms:
        videos = videos.filter(tags__name__icontains=term)

    videos = videos.distinct().order_by('-id')

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'bjj/tag_search_results.html', {
        'query': query,
        'videos': page_obj,
        'video_count': videos.count(),  # ✅ total count
    })
