from django.core.management.base import BaseCommand
from apps.sources.models import Source
from apps.sources.classifier import classify_source_scope


class Command(BaseCommand):
    help = "Dynamically classifies sources into 'موقع يمني', 'موقع عربي', or 'موقع دولي'"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reclassify all sources even if source_type is already set",
        )

    def handle(self, *args, **options):
        force = options["force"]
        sources = Source.objects.all()
        counts = {"موقع يمني": 0, "موقع عربي": 0, "موقع دولي": 0}

        updated = 0
        for s in sources:
            if not force and s.source_type in counts:
                counts[s.source_type] += 1
                continue

            sample_posts = list(s.posts.all()[:20])
            category = classify_source_scope(
                name=s.name,
                website_url=s.website,
                feed_url=s.link,
                brief_info=s.brief_info,
                sample_posts=sample_posts,
            )
            s.source_type = category
            s.save(update_fields=["source_type"])
            counts[category] = counts.get(category, 0) + 1
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully classified {updated} sources: "
                f"{counts.get('موقع يمني', 0)} يمني, "
                f"{counts.get('موقع عربي', 0)} عربي, "
                f"{counts.get('موقع دولي', 0)} دولي."
            )
        )
