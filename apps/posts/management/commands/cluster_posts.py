from django.core.management.base import BaseCommand
from apps.posts.services.clusterer import PostClusterer

class Command(BaseCommand):
    help = 'Clusters recent unclustered posts into topics'

    def handle(self, *args, **options):
        self.stdout.write("Starting clustering process...")
        clusterer = PostClusterer()
        clusterer.clusterize_recent_posts()
        self.stdout.write(self.style.SUCCESS("Clustering completed!"))
