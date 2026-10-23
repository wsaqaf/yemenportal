from django.core.cache import cache
from apps.sources.models import Source
from apps.posts.models import Category

def global_filters(request):
    """
    Caches categories and approved sources in Redis for 2 hours to avoid
    evaluating static metadata on every single page load.
    """
    categories = cache.get_or_set(
        'global_categories_list',
        lambda: list(Category.objects.all().order_by('name')),
        timeout=7200
    )
    sources = cache.get_or_set(
        'global_approved_sources_list',
        lambda: list(Source.objects.filter(approve_state=Source.ApproveState.APPROVED).order_by('name')),
        timeout=7200
    )
    return {
        'all_categories': categories,
        'all_sources': sources,
    }
