import concurrent.futures
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.sources.models import Source
from apps.posts.models import Post
from apps.posts.utils import is_iframe_allowed


class Command(BaseCommand):
    help = "Audits all sources to detect websites that forbid iframe embedding (CSP, X-Frame-Options) and updates iframe_flag."

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Audit all approved sources, not just those currently marked iframe_flag=True',
        )

    def handle(self, *args, **options):
        check_all = options.get('all', False)
        qs = Source.objects.filter(approve_state=Source.ApproveState.APPROVED)
        if not check_all:
            qs = qs.filter(iframe_flag=True)

        sources = list(qs)
        self.stdout.write(f"Auditing iframe permissions for {len(sources)} sources...")

        # Map each source to a test URL (prefer a recent article link, fallback to website)
        recent_post_links = dict(
            Post.objects.filter(source__in=sources)
            .order_by('source_id', '-published_at')
            .distinct('source_id')
            .values_list('source_id', 'link')
        )

        disabled_count = 0
        allowed_count = 0

        def check_source(src):
            test_url = recent_post_links.get(src.id) or src.website or src.link
            if not test_url:
                return src, True, "No URL"
            
            # Clear domain cache before audit if auditing
            import urllib.parse
            domain = urllib.parse.urlparse(test_url).netloc.lower()
            cache.delete(f'iframe_ok_{domain}')

            allowed = is_iframe_allowed(test_url, source=src)
            return src, allowed, test_url

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(check_source, s) for s in sources]
            for future in concurrent.futures.as_completed(futures):
                src, allowed, url = future.result()
                if not allowed:
                    disabled_count += 1
                    self.stdout.write(self.style.WARNING(f"  [BLOCKED] {src.name} -> iframe_flag set to FALSE (URL: {url[:60]})"))
                else:
                    allowed_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Audit finished! {disabled_count} sources blocked/disabled, {allowed_count} sources allowed."
        ))
