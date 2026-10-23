import os
import django
from django.db import connections, transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.posts.models import Post, Category

def migrate_post_categories():
    print("Starting post categories migration...")
    batch_size = 10000
    offset = 0
    
    # Get existing post IDs in current DB to avoid FK errors
    # (Since migration is ongoing, we only want to link categories for posts we already have)
    existing_post_ids = set(Post.objects.values_list('id', flat=True))
    existing_category_ids = set(Category.objects.values_list('id', flat=True))
    
    print(f"Tracking {len(existing_post_ids)} existing posts and {len(existing_category_ids)} categories.")

    while True:
        with connections['legacy'].cursor() as cursor:
            cursor.execute(f"SELECT post_id, category_id FROM post_categories LIMIT {batch_size} OFFSET {offset}")
            rows = cursor.fetchall()
            
            if not rows:
                break
            
            links = []
            for post_id, category_id in rows:
                if post_id in existing_post_ids and category_id in existing_category_ids:
                    links.append((post_id, category_id))
            
            if links:
                with connections['default'].cursor() as django_cursor:
                    # Using raw SQL for bulk insert into join table to avoid Django model overhead for millions of records
                    # The join table is posts_post_categories (post_id, category_id)
                    values_str = ",".join([f"({p}, {c})" for p, c in links])
                    django_cursor.execute(f"INSERT INTO posts_post_categories (post_id, category_id) VALUES {values_str} ON CONFLICT DO NOTHING")
            
            offset += batch_size
            print(f"Processed {offset} category links...")

if __name__ == "__main__":
    migrate_post_categories()
