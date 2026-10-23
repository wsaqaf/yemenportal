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

        total = super().count
        cache.set(cache_key, total, timeout=1800)  # Cache for 30 minutes
        return total
