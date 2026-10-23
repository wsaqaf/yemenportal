import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sources.models import Source
from apps.posts.models import Post
from django.db.models import Count
from django.db import transaction

def cleanup():
    # 1. Strip whitespace from all names first
    print("Trimming whitespace from all source names...")
    for src in Source.objects.all():
        stripped = src.name.strip()
        if src.name != stripped:
            src.name = stripped
            src.save()

    # 2. Delete Junk
    junk_names = ['Ruby', 'Test', 'Test feed', 'Text Feed', 'Text feed', '']
    junk_sources = Source.objects.filter(name__in=junk_names)
    print(f"Deleting {junk_sources.count()} junk source records...")
    junk_sources.delete()

    # 3. Merge Duplicates
    # Re-fetch names after stripping
    all_names = Source.objects.values('name').annotate(name_count=Count('id')).filter(name_count__gt=1)
    
    for entry in all_names:
        name = entry['name']
        sources = list(Source.objects.filter(name=name).order_by('id'))
        master = sources[0]
        duplicates = sources[1:]
        
        print(f"Merging {len(duplicates)} duplicates for '{name}' into Master ID {master.id}...")
        
        with transaction.atomic():
            for dup in duplicates:
                # Move posts
                Post.objects.filter(source=dup).update(source=master)
                # Delete duplicate
                dup.delete()

    print("Cleanup complete!")

if __name__ == "__main__":
    cleanup()
