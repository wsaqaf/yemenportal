from django.core.management.base import BaseCommand
from apps.sources.models import Source
from apps.crawler.fetcher import fetch_source

class Command(BaseCommand):
    help = 'Fetches posts from all valid sources'

    def handle(self, *args, **options):
        sources = Source.objects.filter(approve_state=Source.ApproveState.APPROVED)
        self.stdout.write(f"Fetching from {sources.count()} sources...")
        
        for source in sources:
            self.stdout.write(f"Fetching from {source.name}...")
            count = fetch_source(source)
            self.stdout.write(self.style.SUCCESS(f"Fetched {count} new posts from {source.name}"))
