from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from apps.posts.models import NewsletterOptOut, NewsletterAnnouncement
from apps.posts.newsletter import make_unsub_token

class Command(BaseCommand):
    help = 'Send custom announcement email with strict safety controls'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='ID of NewsletterAnnouncement to send')
        parser.add_argument('--subject', type=str, help='Custom subject')
        parser.add_argument('--body', type=str, help='Custom body text')
        parser.add_argument('--test-email', type=str, help='Send only to this test email address')
        parser.add_argument('--is-test', action='store_true', help='Send only to announcement.test_email')
        parser.add_argument('--tier1-only', action='store_true', help='Send strictly to Tier 1 verified genuine subscribers')
        parser.add_argument('--batch-size', type=int, default=0, help='Max number of emails to send in this batch (0 = all)')
        parser.add_argument('--delay', type=float, default=1.5, help='Delay in seconds between emails to respect SMTP rate limits')
        parser.add_argument('--confirm', action='store_true', help='Explicit confirmation required for mass mailing')

    def handle(self, *args, **options):
        import time
        import re
        from apps.posts.services.subscriber_cleaner import classify_subscribers
        from apps.posts.models import Vote
        announcement_id = options.get('id')
        subject = options.get('subject')
        body = options.get('body')
        test_email = options.get('test_email')
        is_test = options.get('is_test', False)
        confirm = options.get('confirm', False)
        is_html = False
        announcement = None

        if announcement_id:
            try:
                announcement = NewsletterAnnouncement.objects.get(id=announcement_id)
                subject = announcement.subject
                body = announcement.body
                is_html = announcement.is_html
                if is_test and announcement.test_email:
                    test_email = announcement.test_email
            except NewsletterAnnouncement.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Announcement #{announcement_id} not found.'))
                return

        if not subject or not body:
            self.stdout.write(self.style.ERROR('Please provide either --id or both --subject and --body.'))
            return

        # 🔒 صمام الأمان: منع الإرسال الجماعي دون تأكيد صريح
        if not test_email and not confirm:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  تنبيه أمان: أنت على وشك الإرسال الجماعي للأعضاء!\n"
                "• للتجربة على بريدك الشخصي فقط، استخدم: --test-email=your@email.com أو --is-test\n"
                "• للموافقة على الإرسال الفعلي، أضف الراية: --confirm\n"
            ))
            return

        site_url = 'https://yemenportal.net'
        User = get_user_model()
        opted_out = set(NewsletterOptOut.objects.values_list('email', flat=True))

        tier1_only = options.get('tier1_only', False)
        batch_size = options.get('batch_size', 0)
        delay = options.get('delay', 1.5)

        if test_email:
            recipients = [test_email]
        elif announcement and announcement.target_group == 'staff_only':
            all_users = User.objects.filter(is_active=True, is_staff=True).exclude(email='').values_list('email', flat=True)
            recipients = [e for e in set(all_users) if e.lower() not in opted_out]
            self.stdout.write(self.style.SUCCESS(f"Selected {len(recipients)} staff/admin recipients."))
        elif announcement and announcement.target_group == 'active_only':
            voter_ids = set(Vote.objects.values_list('user_id', flat=True))
            login_ids = set(User.objects.exclude(last_login=None).values_list('id', flat=True))
            active_ids = voter_ids | login_ids
            all_users = User.objects.filter(id__in=active_ids, is_active=True).exclude(email='').values_list('email', flat=True)
            recipients = [e for e in set(all_users) if e.lower() not in opted_out]
            self.stdout.write(self.style.SUCCESS(f"Selected {len(recipients)} active (voters/login) recipients."))
        elif announcement and announcement.target_group == 'custom':
            raw = announcement.custom_recipients or ''
            custom_list = [e.strip() for e in re.split(r'[\r\n,;]+', raw) if e.strip() and '@' in e]
            recipients = [e for e in set(custom_list) if e.lower() not in opted_out]
            self.stdout.write(self.style.SUCCESS(f"Selected {len(recipients)} custom specified recipients."))
        elif tier1_only:
            classified = classify_subscribers()
            recipients = [item['email'] for item in classified['tier1'] if item['email'].lower() not in opted_out]
            self.stdout.write(self.style.SUCCESS(f"Selected {len(recipients)} Tier 1 verified genuine recipients."))
        else:
            all_users = User.objects.filter(is_active=True).exclude(email='').values_list('email', flat=True)
            recipients = [e for e in set(all_users) if e.lower() not in opted_out]

        if batch_size > 0:
            recipients = recipients[:batch_size]

        self.stdout.write(f'Sending to {len(recipients)} recipient(s) (delay: {delay}s)...')
        success_count = 0

        for idx, email in enumerate(recipients, 1):
            if idx > 1 and delay > 0:
                time.sleep(delay)

            token = make_unsub_token(email)
            unsub_url = f"{site_url}{reverse('posts:newsletter_unsubscribe', kwargs={'token': token})}"

            html_body = render_to_string('newsletter/announcement_email.html', {
                'subject': subject,
                'body': body,
                'is_html': is_html,
                'site_url': site_url,
                'unsub_url': unsub_url,
            })

            msg = EmailMultiAlternatives(
                subject=subject,
                body=f'{subject}\n\n{body}\n\nلإلغاء الاشتراك: {unsub_url}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@yemenportal.net'),
                to=[email],
                headers={
                    'List-Unsubscribe': f'<{unsub_url}>',
                    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
                }
            )
            msg.attach_alternative(html_body, 'text/html')
            try:
                msg.send(fail_silently=False)
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'• Sent to: {email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'• Failed for {email}: {e}'))

        if announcement and not test_email:
            announcement.status = 'sent'
            announcement.recipients_count = success_count
            announcement.sent_at = timezone.now()
            announcement.save(update_fields=['status', 'recipients_count', 'sent_at'])
            self.stdout.write(self.style.SUCCESS(f'Announcement #{announcement.id} recorded with {success_count} sends.'))
