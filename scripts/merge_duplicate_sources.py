import django
import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.sources.models import Source
from apps.posts.models import Post
from django.db.models import Count

def merge_duplicates():
    print("Starting duplicate source merge...")
    duplicates = Source.objects.values('name').annotate(name_count=Count('id')).filter(name_count__gt=1)
    
    for dup in duplicates:
        name = dup['name']
        if not name: continue
        
        # Get all sources with this name, ordered by post count (descending)
        sources = list(Source.objects.filter(name=name).annotate(post_count=Count('posts')).order_by('-post_count'))
        
        if len(sources) < 2: continue
        
        master = sources[0]
        others = sources[1:]
        
        print(f"Merging {len(others)} sources into master: {master.name} (ID: {master.id})")
        
        for other in others:
            # Move posts to master
            Post.objects.filter(source=other).update(source=master)
            # Delete the duplicate source
            other.delete()
            
    print("Duplicate merge complete.")

if __name__ == "__main__":
    merge_duplicates()
