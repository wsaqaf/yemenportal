from celery import shared_task
from apps.sources.models import Source
from .fetcher import fetch_source

@shared_task
def crawl_all_sources():
    sources = Source.objects.filter(state=Source.State.VALID, approve_state=Source.ApproveState.APPROVED)
    for source in sources:
        fetch_source_task.delay(source.id)

@shared_task
def fetch_source_task(source_id):
    try:
        source = Source.objects.get(id=source_id)
        fetch_source(source)
    except Source.DoesNotExist:
        pass
