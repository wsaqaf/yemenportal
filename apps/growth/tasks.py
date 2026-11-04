import logging
from celery import shared_task
from .services.telegram_service import (
    publish_next_hot_cluster,
    publish_morning_exchange_rates,
)

logger = logging.getLogger(__name__)


@shared_task(name="apps.growth.tasks.broadcast_telegram_hot_clusters")
def broadcast_telegram_hot_clusters(min_sources=3, max_per_run=1):
    """
    Celery task that checks for newly formed or trending news clusters
    covered by at least `min_sources` news outlets and broadcasts them to Telegram.
    """
    try:
        results = publish_next_hot_cluster(min_sources=min_sources, max_per_run=max_per_run)
        logger.info(f"Broadcasted {len(results)} hot clusters to Telegram.")
        return results
    except Exception as e:
        logger.error(f"Error in broadcast_telegram_hot_clusters: {e}")
        return []


@shared_task(name="apps.growth.tasks.broadcast_telegram_morning_exchange_rates")
def broadcast_telegram_morning_exchange_rates():
    """
    Celery task that broadcasts daily morning currency exchange rates
    for Sana'a and Aden in a distinct box style.
    """
    try:
        res = publish_morning_exchange_rates(force=False)
        logger.info(f"Morning exchange rates task result: {res}")
        return res
    except Exception as e:
        logger.error(f"Error in broadcast_telegram_morning_exchange_rates: {e}")
        return {'status': 'error', 'error': str(e)}
