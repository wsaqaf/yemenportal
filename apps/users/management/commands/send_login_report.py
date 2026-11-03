from django.core.management.base import BaseCommand
from apps.users.tasks import generate_login_report


class Command(BaseCommand):
    help = "Generates and sends an email report of users who logged in within the past specified hours."

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@yemenportal.net',
            help='Recipient email address (default: admin@yemenportal.net)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Lookback window in hours (default: 24)'
        )

    def handle(self, *args, **options):
        email = options['email']
        hours = options['hours']
        self.stdout.write(f"Generating login report for the past {hours} hours to {email}...")
        try:
            result = generate_login_report(hours=hours, recipient=email)
            self.stdout.write(self.style.SUCCESS(f"Successfully executed: {result}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send login report: {e}"))
