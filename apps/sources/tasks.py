import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from apps.sources.models import Source, SourceLog

logger = logging.getLogger(__name__)

@shared_task(name="apps.sources.tasks.audit_and_cleanup_sources")
def audit_and_cleanup_sources():
    """
    Periodic task to detect failing RSS feeds, deactivate dead sources,
    and prune stale crawler logs.
    """
    now = timezone.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_14d = now - timedelta(days=14)

    # 1. Identify sources with >= 50 errors in the last 24h
    failing_sources = (
        SourceLog.objects.filter(created_at__gte=cutoff_24h, state__startswith='Error')
        .values('source_id')
        .annotate(error_count=models.Count('id'))
        if hasattr(models, 'Count') else []
    )

    from django.db.models import Count
    failing = (
        SourceLog.objects.filter(created_at__gte=cutoff_24h, state__startswith='Error')
        .values('source_id')
        .annotate(error_count=Count('id'))
        .filter(error_count__gte=50)
    )

    deactivated = []
    for item in failing:
        sid = item['source_id']
        source = Source.objects.filter(id=sid, state='valid').first()
        if source:
            source.state = 'invalid'
            source.save(update_fields=['state'])
            deactivated.append(f"{source.name} ({item['error_count']} errors)")
            logger.warning(f"Quarantined dead source {source.name} (ID: {sid}) due to {item['error_count']} errors.")

    # 2. Prune sourcelogs older than 14 days
    deleted_logs, _ = SourceLog.objects.filter(created_at__lt=cutoff_14d).delete()
    logger.info(f"Pruned {deleted_logs} crawler logs older than 14 days.")

    result_msg = f"Deactivated {len(deactivated)} failing sources. Pruned {deleted_logs} old logs."
    return result_msg
