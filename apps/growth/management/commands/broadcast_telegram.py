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
            default=8,
            help='Minimum distinct sources for major clusters (default: 8)'
        )
        parser.add_argument(
            '--urgent-min-sources',
            type=int,
            default=5,
            help='Minimum distinct sources for urgent/breaking clusters (default: 5)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=1,
            help='Maximum number of clusters to publish in this run (default: 1)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=12,
            help='Lookback window in hours for clusters (default: 12)'
        )

    def handle(self, *args, **options):
        b_type = options['type']
        force = options['force']
        min_sources = options['min_sources']
        urgent_min_sources = options['urgent_min_sources']
        hours = options['hours']
        limit = options['limit']

        if b_type in ['rates', 'all']:
            self.stdout.write("Publishing morning exchange rates...")
            res = publish_morning_exchange_rates(force=force)
            self.stdout.write(f"Exchange Rates result: {res}")

        if b_type in ['clusters', 'all']:
            self.stdout.write(
                f"Publishing up to {limit} high-priority clusters "
                f"(major>={min_sources}, urgent>={urgent_min_sources} distinct sources)..."
            )
            res = publish_next_hot_cluster(
                min_sources=min_sources,
                urgent_min_sources=urgent_min_sources,
                max_per_run=limit,
                hours=hours,
                respect_limits=not force,
            )
            self.stdout.write(f"Clusters result: {res}")

        self.stdout.write(self.style.SUCCESS("Broadcast operation completed."))
