from django.core.management.base import BaseCommand
from apps.sources.models import Source, SourceLog
from django.db.models import Max

class Command(BaseCommand):
    help = 'List RSS sources that are failing to fetch.'

    def handle(self, *args, **options):
        # Get the latest log for each source
        latest_logs = SourceLog.objects.values('source_id').annotate(latest_id=Max('id'))
        latest_log_ids = [item['latest_id'] for item in latest_logs]
        
        logs = SourceLog.objects.filter(id__in=latest_log_ids).select_related('source')
        
        failing = []
        for log in logs:
            if log.state and log.state.startswith('Error'):
                failing.append(log)
        
        if not failing:
            self.stdout.write(self.style.SUCCESS("All checked sources are working fine!"))
            return

        self.stdout.write(self.style.ERROR(f"Found {len(failing)} failing sources:"))
        for log in failing:
            self.stdout.write(f"- {log.source.name} ({log.source.link})")
            self.stdout.write(self.style.WARNING(f"  Reason: {log.state}"))
            self.stdout.write("")
