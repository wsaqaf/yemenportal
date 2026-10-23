
import hashlib
from celery import shared_task
from django.core.cache import cache
from apps.posts.models import Post, Category

@shared_task(name="apps.posts.tasks.prewarm_category_counts")
def prewarm_category_counts():
    """Pre-warms CachedCountPaginator keys for all active categories in Redis."""
    categories = Category.objects.all()
    warmed = 0
    for cat in categories:
        qs = Post.objects.filter(state=Post.State.APPROVED, categories__id__in=[str(cat.id)]).order_by('-published_at')
        query_hash = hashlib.md5(str(qs.query).encode('utf-8')).hexdigest()
        cache_key = f"paginator_count_{query_hash}"
        total = qs.count()
        cache.set(cache_key, total, timeout=3600 * 12)  # 12-hour TTL
        warmed += 1
    return f"Pre-warmed {warmed} category counts in Redis."

@shared_task(name="apps.posts.tasks.cluster_recent_posts")
def cluster_recent_posts():
    """Periodic task to cluster recent unassigned posts into topics."""
    from apps.posts.services.clusterer import PostClusterer
    clusterer = PostClusterer()
    clusterer.clusterize_recent_posts()
    return "Batch clustering completed."
