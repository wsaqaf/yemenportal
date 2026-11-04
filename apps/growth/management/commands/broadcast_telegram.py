from django.core.management.base import BaseCommand
from apps.growth.services.telegram_service import (
    publish_next_hot_cluster,
    publish_morning_exchange_rates,
)


class Command(BaseCommand):
    help = "Broadcasts hot clusters or daily exchange rates to the official Telegram channel"

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['rates', 'clusters', 'all'],
            default='clusters',
            help='What content to broadcast: rates, clusters, or all'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force broadcast even if already sent today'
        )
        parser.add_argument(
            '--min-sources',
            type=int,
            default=3,
            help='Minimum number of sources in cluster (default: 3)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=72,
            help='Lookback window in hours for clusters (default: 72)'
        )

    def handle(self, *args, **options):
        b_type = options['type']
        force = options['force']
        min_sources = options['min_sources']
        hours = options['hours']

        if b_type in ['rates', 'all']:
            self.stdout.write("Publishing morning exchange rates...")
            res = publish_morning_exchange_rates(force=force)
            self.stdout.write(f"Exchange Rates result: {res}")

        if b_type in ['clusters', 'all']:
            self.stdout.write(f"Publishing hot clusters (min {min_sources} sources)...")
            res = publish_next_hot_cluster(min_sources=min_sources, max_per_run=1, hours=hours)
            self.stdout.write(f"Clusters result: {res}")

        self.stdout.write(self.style.SUCCESS("Broadcast operation completed."))
