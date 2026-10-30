from django.core.management.base import BaseCommand
from apps.posts.services.subscriber_cleaner import classify_subscribers, sync_tier3_to_optout
from apps.posts.models import NewsletterOptOut


class Command(BaseCommand):
    help = 'Audits subscribers into 3 safety tiers and shields Amazon SES by excluding bots and dead emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Add Tier 3 spam/bot/defunct emails to NewsletterOptOut table',
        )
        parser.add_argument(
            '--show-tier1',
            action='store_true',
            help='Display all Tier 1 verified genuine subscribers',
        )
        parser.add_argument(
            '--show-tier3',
            action='store_true',
            help='Display sample of Tier 3 spam/bot accounts',
        )

    def handle(self, *args, **options):
        self.stdout.write("Auditing and classifying subscribers...")
        results = classify_subscribers()
        t1 = results['tier1']
        t2 = results['tier2']
        t3 = results['tier3']
        total = len(t1) + len(t2) + len(t3)

        self.stdout.write(self.style.SUCCESS(f"\n======================================================="))
        self.stdout.write(self.style.SUCCESS(f"🛡️  SUBSCRIBER AUDIT & SAFETY REPORT"))
        self.stdout.write(self.style.SUCCESS(f"======================================================="))
        self.stdout.write(f"Total Subscribers: {total}")
        self.stdout.write(self.style.SUCCESS(f"  • Tier 1 (Genuine / Active / Verified): {len(t1)} ({len(t1)/total*100:.2f}%)"))
        self.stdout.write(self.style.WARNING(f"  • Tier 2 (Unconfirmed Legacy):           {len(t2)} ({len(t2)/total*100:.2f}%)"))
        self.stdout.write(self.style.ERROR(  f"  • Tier 3 (Spam Bots / Scraper / Dead):   {len(t3)} ({len(t3)/total*100:.2f}%)"))

        if options.get('show_tier1'):
            self.stdout.write(self.style.SUCCESS(f"\n--- TIER 1 VERIFIED USERS ({len(t1)}) ---"))
            for item in t1:
                name_str = f" [{item.get('full_name')}]" if item.get('full_name') else ""
                self.stdout.write(f"  ✓ {item['email']}{name_str} ({item.get('reason', '')})")

        if options.get('show_tier3'):
            self.stdout.write(self.style.ERROR(f"\n--- TIER 3 DETECTED BOTS/SPAM SAMPLES ({len(t3)}) ---"))
            for item in t3[:30]:
                self.stdout.write(f"  ✗ {item['email']} -> {item.get('reason')}")

        if options.get('apply'):
            count = sync_tier3_to_optout()
            self.stdout.write(self.style.SUCCESS(f"\n[APPLIED] Successfully added {count} Tier 3 emails to NewsletterOptOut exclusion list."))
            total_opted_out = NewsletterOptOut.objects.count()
            self.stdout.write(self.style.SUCCESS(f"Total emails now permanently shielded from mailings: {total_opted_out}"))
        else:
            self.stdout.write(self.style.NOTICE("\nRun with '--apply' to automatically shield Amazon SES by adding Tier 3 emails to NewsletterOptOut."))
