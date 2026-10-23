import os
import django
from django.db import connections, transaction, models

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.posts.models import Post, Vote, PostView
from apps.users.models import User

def migrate_votes_and_metrics():
    print("Starting votes and metrics migration...")
    
    # 1. Migrate Votes table
    print("Migrating Vote table...")
    with connections['legacy'].cursor() as cursor:
        cursor.execute("SELECT id, user_id, post_id, value, created_at, updated_at FROM votes")
        rows = cursor.fetchall()
        
        # Get existing user and post IDs to avoid FK errors
        existing_users = set(User.objects.values_list('id', flat=True))
        existing_posts = set(Post.objects.values_list('id', flat=True))
        
        votes = []
        for row in rows:
            if row[1] in existing_users and row[2] in existing_posts:
                votes.append(Vote(
                    id=row[0],
                    user_id=row[1],
                    post_id=row[2],
                    value=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                ))
        
        if votes:
            Vote.objects.bulk_create(votes, ignore_conflicts=True)
            print(f"Migrated {len(votes)} votes.")

    # 2. Update Post metrics (voting_result and post_views_count)
    # Since bulk_create skipped existing posts, we need to sync these columns
    print("Syncing Post metrics (voting_result and post_views_count)...")
    batch_size = 5000
    offset = 0
    
    while True:
        with connections['legacy'].cursor() as cursor:
            cursor.execute(f"SELECT id, voting_result, post_views_count FROM posts ORDER BY id DESC LIMIT {batch_size} OFFSET {offset}")
            rows = cursor.fetchall()
            
            if not rows:
                break
            
            # We only care about posts we actually have in our DB
            updates = []
            for post_id, v_res, p_views in rows:
                if post_id in existing_posts:
                    updates.append(Post(id=post_id, voting_result=v_res, post_views_count=p_views))
            
            if updates:
                # Bulk update existing records
                Post.objects.bulk_update(updates, ['voting_result', 'post_views_count'])
            
            offset += batch_size
            if offset % 50000 == 0:
                print(f"Synced metrics for {offset} posts...")

    print("Migration and sync complete!")

if __name__ == "__main__":
    migrate_votes_and_metrics()
