from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from apps.posts.models import Post, NewsletterOptOut
from apps.posts.newsletter import make_unsub_token

class Command(BaseCommand):
    help = 'Send YemenPortal news digest with RFC 8058 one-click unsubscribe support'

    def add_arguments(self, parser):
        parser.add_argument('--test-email', type=str, help='Send a test email to this address only')
        parser.add_argument('--limit', type=int, default=10, help='Number of posts to include')

    def handle(self, *args, **options):
        test_email = options.get('test_email')
        limit = options.get('limit')
        site_url = 'http://194.163.154.154'

        posts = Post.objects.filter(state=Post.State.APPROVED).select_related('source').order_by('-published_at')[:limit]
        if not posts:
            self.stdout.write(self.style.WARNING('No approved posts found.'))
            return

        if test_email:
            targets = [test_email]
        else:
            User = get_user_model()
            opted_out = set(NewsletterOptOut.objects.values_list('email', flat=True))
            all_users = User.objects.exclude(email='').values_list('email', flat=True)
            targets = [e for e in set(all_users) if e.lower() not in opted_out]

        self.stdout.write(f'Sending newsletter to {len(targets)} recipient(s)...')

        for email in targets:
            token = make_unsub_token(email)
            unsub_url = f"{site_url}{reverse('posts:newsletter_unsubscribe', kwargs={'token': token})}"

            html_body = render_to_string('newsletter/digest_email.html', {
                'posts': posts,
                'site_url': site_url,
                'unsub_url': unsub_url,
            })

            msg = EmailMultiAlternatives(
                subject='نشرة يمن بورتال: أبرز المستجدات الإخبارية',
                body=f'لقراءة النشرة الإخبارية يرجى زيارة: {site_url}\nلإلغاء الاشتراك: {unsub_url}',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@yemenportal.net'),
                to=[email],
                headers={
                    'List-Unsubscribe': f'<{unsub_url}>',
                    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
                }
            )
            msg.attach_alternative(html_body, "text/html")
            try:
                msg.send(fail_silently=False)
                self.stdout.write(self.style.SUCCESS(f'• Sent to: {email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'• Failed to send to {email}: {e}'))
