import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'fetch-rss-every-10-minutes': {
        'task': 'apps.crawler.tasks.crawl_all_sources',
        'schedule': crontab(minute='*/10'),
    },
    'cluster-posts-every-15-minutes': {
        'task': 'apps.posts.tasks.cluster_recent_posts',
        'schedule': crontab(minute='*/15'),
    },
    'prewarm-category-counts-every-6h': {
        'task': 'apps.posts.tasks.prewarm_category_counts',
        'schedule': crontab(minute='0', hour='*/6'),
    },
    'audit-sources-daily-2am': {
        'task': 'apps.sources.tasks.audit_and_cleanup_sources',
        'schedule': crontab(minute='0', hour='2'),
    },
    'maintain-database-vacuum-daily-3am': {
        'task': 'apps.posts.tasks.maintain_database_indexes',
        'schedule': crontab(minute='0', hour='3'),
    },
    'refresh-portal-services-every-30m': {
        'task': 'apps.posts.tasks.refresh_portal_services_cache',
        'schedule': crontab(minute='*/30'),
    },
}
