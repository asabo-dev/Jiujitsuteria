import os
import django
from pathlib import Path
import boto3
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jiujitsuteria.settings')
django.setup()

from bjj.models import Video, Tag

# AWS & Local setup
s3 = boto3.client('s3')
bucket_name = 'jiujitsuteria-videos'
local_folder = Path('/Users/quanefiom/Desktop/BJJ_app')

# S3 base URL
s3_base_url = f"https://{bucket_name}.s3.amazonaws.com/"

# Define tag keywords (you can expand this list)
KNOWN_TAGS = [
    'gi', 'no_gi', 'armbar', 'triangle', 'mount', 'guard', 'pass',
    'prof_ali', 'prof_daniel', 'takedown', 'sweep', 'kimura', 'americana'
]

def extract_tags_from_filename(filename: str):
    """Extract known tags from the filename (lowercase, underscore separated)."""
    tags_found = []
    clean_name = filename.lower().replace(' ', '_')
    for tag in KNOWN_TAGS:
        if tag in clean_name:
            tags_found.append(tag)
    return tags_found

def upload_and_save_videos(local_folder):
    for local_path in local_folder.rglob('*.mp4'):
        s3_key = str(local_path.relative_to(local_folder)).replace(' ', '_')
        print(f"📤 Uploading {local_path} as {s3_key}...")

        # Upload to S3
        s3.upload_file(
            str(local_path),
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': 'video/mp4'}
        )

        # S3 URL
        s3_url = s3_base_url + s3_key

        # Format title and extract tags
        title = local_path.stem.replace('_', ' ').title()
        raw_tags = extract_tags_from_filename(local_path.stem)

        # Save to DB
        video = Video.objects.create(
            title=title,
            video_url=s3_url
        )

        # Add tags (create if not exist)
        for tag_name in raw_tags:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
            video.tags.add(tag_obj)

        print(f"✅ Saved: {title} → {s3_url} with tags: {', '.join(raw_tags) or 'none'}")

upload_and_save_videos(local_folder)
print("🎉 All videos uploaded and saved to the database with tags.")
