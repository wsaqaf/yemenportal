
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

@shared_task(name="apps.posts.tasks.maintain_database_indexes")
def maintain_database_indexes():
    """
    Scheduled maintenance: cleans GIN trigram pending list and runs
    VACUUM ANALYZE to prevent index bloat and update planner statistics.
    """
    from django.db import connection
    logger.info("Starting scheduled database vacuum and GIN maintenance...")

    # 1. Flush GIN pending list for fast search reads
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT gin_clean_pending_list('idx_posts_approved_title_trgm');")
            cleaned_pages = cursor.fetchone()[0]
            logger.info(f"Cleaned {cleaned_pages} pages from GIN trigram index pending list.")
        except Exception as e:
            logger.warning(f"Could not clean GIN pending list: {e}")

    # 2. Run VACUUM (ANALYZE) in autocommit mode
    old_autocommit = connection.get_autocommit()
    connection.set_autocommit(True)
    try:
        with connection.cursor() as cursor:
            cursor.execute("VACUUM (ANALYZE) posts_post;")
            cursor.execute("VACUUM (ANALYZE) sources_sourcelog;")
        logger.info("VACUUM (ANALYZE) completed successfully.")
    finally:
        connection.set_autocommit(old_autocommit)

    return "Database and index maintenance completed."
