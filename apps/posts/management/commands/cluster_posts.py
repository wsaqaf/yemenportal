from django.core.management.base import BaseCommand
from apps.posts.services.clusterer import PostClusterer

class Command(BaseCommand):
    help = 'Clusters recent unclustered posts into topics with smart 4-hour window'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=4,
            help='Lookback hours for clustering window (default: 4)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-clustering the window from scratch'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        force = options['force']
        self.stdout.write(f"Starting clustering process (window={hours}h, force={force})...")
        clusterer = PostClusterer()
        clusterer.LOOKBACK_HOURS = hours
        count = clusterer.clusterize_recent_posts(unclustered_hours=hours, force_recluster=force)
        self.stdout.write(self.style.SUCCESS(f"Clustering completed! {count} posts clustered."))
