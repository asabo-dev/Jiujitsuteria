"""Views for Brazilian Jiu-Jitsu (BJJ) video management and display.
Includes video upload, listing, categorization, and searching by tags."""

import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q

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
def upload_video(request):          # I need to fix this function
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
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


"""
Fallback simple tag search (term-based, not multi-word aware)
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
    })"""


STOPWORDS = {"from", "in", "on", "at", "the", "a", "an", "of", "and", "with"}

# ✅ Add a synonyms dictionary
SYNONYMS = {
    "no gi": "nogi",
    "no-gi": "nogi",
}

def extract_tags_from_query(query): #nogi querries need to be fixed!
    """Match query text against DB tags (multi-word aware)."""
    query = query.lower().strip()
    query = re.sub(r"[^\w\s]", " ", query)  # strip punctuation

    # Load all tag names once
    tag_names = list(Tag.objects.values_list("name", flat=True))
    tag_map = {t.lower(): t for t in tag_names}  # lowercase → canonical tag

    matched_tags = []
    used_tokens = set()

    # First: check full multi-word tags (longest tags first)
    for tag in sorted(tag_map.keys(), key=len, reverse=True):
        if tag in query and tag not in used_tokens:
            matched_tags.append(tag_map[tag])
            used_tokens.update(tag.split())

    # Second: check leftover single terms
    terms = [t for t in query.split() if t not in STOPWORDS and t not in used_tokens]
    for term in terms:
        if term in tag_map:
            matched_tags.append(tag_map[term])

    return matched_tags

def tag_search(request):
    query = request.GET.get("q", "").strip().lower()
    matched_tags = extract_tags_from_query(query)

    videos = Video.objects.all()
    for tag in matched_tags:
        videos = videos.filter(tags__name__iexact=tag)

    videos = videos.distinct().order_by("-id")

    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "bjj/tag_search_results.html", {
        "query": query,
        "videos": page_obj,
        "video_count": videos.count(),
        "matched_tags": matched_tags,  # ✅ useful for debugging or display
    })

