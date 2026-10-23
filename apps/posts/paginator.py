import hashlib
from django.core.paginator import Paginator
from django.core.cache import cache

class CachedCountPaginator(Paginator):
    """
    Caches total object count in Redis using deterministic MD5 query hashing.
    Prevents expensive COUNT(*) full table scans on multi-million row datasets.
    """
    @property
    def count(self):
        query_str = str(self.object_list.query)
        query_hash = hashlib.md5(query_str.encode('utf-8')).hexdigest()
        cache_key = f"paginator_count_{query_hash}"

        cached_count = cache.get(cache_key)
        if cached_count is not None:
            return cached_count

        # For text searches (LIKE/ILIKE), sample up to 501 rows without ordering
        # to allow PostgreSQL to satisfy the check via the GIN trigram index instantly.
        if "LIKE" in query_str or "~~" in query_str:
            sample_count = self.object_list.order_by().values('id')[:501].count()
            cache.set(cache_key, sample_count, timeout=3600)
            return sample_count

        total = super().count
        cache.set(cache_key, total, timeout=1800)  # Cache for 30 minutes
        return total
