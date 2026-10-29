import hashlib
from celery import shared_task
from django.core.cache import cache
from apps.posts.models import Post, Category

@shared_task(name="apps.posts.tasks.prewarm_category_counts")
def prewarm_category_counts():
    """Pre-warms direct category count keys in Redis to make filtering instant."""
    categories = Category.objects.all()
    warmed = 0
    for cat in categories:
        total = Post.objects.filter(categories=cat, state=Post.State.APPROVED).count()
        cache.set(f"category_count_{cat.id}", total, timeout=86400)
        warmed += 1
    return f"Pre-warmed {warmed} category counts in Redis."

@shared_task(name="apps.posts.tasks.cluster_recent_posts")
def cluster_recent_posts():
    """Periodic task to cluster recent unassigned posts into topics."""
    from apps.posts.services.clusterer import PostClusterer
    clusterer = PostClusterer()
    clusterer.clusterize_recent_posts()
    return "Batch clustering completed."

@shared_task(name="apps.posts.tasks.maintain_database_indexes")
def maintain_database_indexes():
    """Daily index maintenance to keep search indices fast."""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("VACUUM ANALYZE posts_post;")
    return "Maintenance complete."
