from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.core.management import call_command
from apps.users.models import User
from apps.users.tasks import generate_login_report


class LoginReportTests(TestCase):
    def setUp(self):
        self.user1 = User(email="active_user@example.com")
        self.user1.set_password("pass123")
        self.user1.last_login = timezone.now() - timedelta(hours=2)
        self.user1.save()

        self.user2 = User(email="old_user@example.com")
        self.user2.set_password("pass123")
        self.user2.last_login = timezone.now() - timedelta(days=5)
        self.user2.date_joined = timezone.now() - timedelta(days=10)
        self.user2.save()

    def test_generate_login_report_sends_email(self):
        generate_login_report(hours=24, recipient="admin@yemenportal.net")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ["admin@yemenportal.net"])
        self.assertIn("تقرير تسجيلات الدخول", email.subject)
        self.assertIn("active_user@example.com", email.body)
        self.assertNotIn("old_user@example.com", email.body)

    def test_management_command_send_login_report(self):
        call_command('send_login_report', email='admin@yemenportal.net', hours=24)
        self.assertEqual(len(mail.outbox), 1)
