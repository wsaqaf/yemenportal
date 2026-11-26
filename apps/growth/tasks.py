import logging
from celery import shared_task
from .services.telegram_service import (
    publish_next_hot_cluster,
    publish_morning_exchange_rates,
)

logger = logging.getLogger(__name__)


@shared_task(name="apps.growth.tasks.broadcast_telegram_hot_clusters")
def broadcast_telegram_hot_clusters(
    min_sources=6,
    urgent_min_sources=4,
    max_per_run=1,
    hours=12,
    cooldown_minutes=45,
    urgent_cooldown_minutes=15,
    max_daily_posts=20,
):
    """
    Celery task that checks for urgent or highly important news clusters
    covered by enough distinct news outlets and broadcasts them to Telegram
    with cooldown and daily cap protections against notification fatigue.
    """
    try:
        results = publish_next_hot_cluster(
            min_sources=min_sources,
            urgent_min_sources=urgent_min_sources,
            max_per_run=max_per_run,
            hours=hours,
            cooldown_minutes=cooldown_minutes,
            urgent_cooldown_minutes=urgent_cooldown_minutes,
            max_daily_posts=max_daily_posts,
        )
        logger.info(f"Broadcasted {len(results)} high-priority clusters to Telegram.")
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
