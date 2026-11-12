import hashlib
from django.core.paginator import Paginator
from django.core.cache import cache

class CachedCountPaginator(Paginator):
    """
    Caches total object count in Redis using deterministic MD5 query hashing.
    Prevents expensive COUNT(*) full table scans on multi-million row datasets.
    """
    SAMPLE_LIMIT = 1001

    @property
    def count(self):
        query_str = str(self.object_list.query)
        query_hash = hashlib.md5(query_str.encode('utf-8')).hexdigest()
        cache_key = f"paginator_count_{query_hash}"

        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count

        # Check if query has search terms or selective filters (sources, categories, topics)
        has_selective_filters = any(
            token in query_str for token in (
                "LIKE", "~~", "source_id", "categories", "topic_id", "voting_result", "post_views_count"
            )
        )

        if has_selective_filters:
            # Slicing with [:1001] generates a subquery with LIMIT 1001 in PostgreSQL,
            # stopping index traversal immediately once 1001 items are found.
            # This provides instant pagination (up to 50 pages of 20 items) in under 1ms
            # instead of locking worker threads with a 30-second full table scan.
            try:
                sample_count = self.object_list.order_by().values('id')[:self.SAMPLE_LIMIT].count()
                cache.set(cache_key, sample_count, timeout=3600)
                return sample_count
            except Exception:
                pass

        total = super().count
        cache.set(cache_key, total, timeout=1800)  # Cache for 30 minutes
        return total
