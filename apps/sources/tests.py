from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from apps.posts.models import Post
from apps.sources.classifier import classify_source_scope
from apps.sources.forms import SourceSuggestionForm
from apps.sources.models import Source, SourceLog


class SourceClassifierTests(TestCase):
    def test_classify_yemeni_source(self):
        res = classify_source_scope(
            name="مأرب برس",
            website_url="https://marebpress.net",
            feed_url="https://marebpress.net/rss.php",
        )
        self.assertEqual(res, "موقع يمني")

        res_ye = classify_source_scope(
            name="وكالة سبأ",
            website_url="https://sabanew.net",
            feed_url="https://sabanew.net/rss.xml",
        )
        self.assertEqual(res_ye, "موقع يمني")

    def test_classify_international_source(self):
        res_bbc = classify_source_scope(
            name="بي بي سي عربي",
            website_url="https://www.bbc.com/arabic",
            feed_url="https://feeds.bbci.co.uk/arabic/rss.xml",
        )
        self.assertEqual(res_bbc, "موقع دولي")

        res_rt = classify_source_scope(
            name="روسيا اليوم",
            website_url="https://arabic.rt.com",
            feed_url="https://arabic.rt.com/rss",
        )
        self.assertEqual(res_rt, "موقع دولي")

    def test_classify_arab_source(self):
        res_arab = classify_source_scope(
            name="اليوم السابع",
            website_url="https://www.youm7.com",
            feed_url="https://www.youm7.com/rss/SectionRss?SectionID=65",
        )
        self.assertEqual(res_arab, "موقع عربي")

    def test_classify_from_feed_content(self):
        class DummyEntry:
            def __init__(self, title, summary):
                self.title = title
                self.summary = summary

        entries = [
            DummyEntry("مجلس القيادة الرئاسي اليمني يجتمع في عدن", "ناقش العليمي الأوضاع الاقتصادية"),
            DummyEntry("أسعار صرف الريال اليمني في صنعاء وعدن اليوم", "تراجع جديد لأسعار العملات"),
            DummyEntry("قوات الجيش الوطني في تعز تصد هجوماً", "معارك في جبهات تعز"),
        ]
        res = classify_source_scope(
            name="صحيفة الأخبار الجديدة",
            website_url="https://newnews.com",
            feed_url="https://newnews.com/feed",
            feed_entries=entries,
        )
        self.assertEqual(res, "موقع يمني")


class SourceSuggestionFormTests(TestCase):
    def test_source_type_not_in_form(self):
        form = SourceSuggestionForm()
        self.assertNotIn("source_type", form.fields)
        self.assertIn("name", form.fields)
        self.assertIn("link", form.fields)
        self.assertIn("website", form.fields)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SourceManagementAndModerationTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="staff_admin",
            email="staff@yemenportal.net",
            password="testpassword123",
            is_staff=True,
        )
        self.submitter = User.objects.create_user(
            username="submitter",
            email="submitter@example.com",
            password="testpassword123",
        )
        self.source = Source.objects.create(
            name="صنعاء نت",
            link="https://sanaanet.net/feed/",
            website="https://sanaanet.net/",
            user=self.submitter,
            state=Source.State.INVALID,
            approve_state=Source.ApproveState.SUGGESTED,
        )

    def test_manage_list_computes_page_metrics_and_logs(self):
        now = timezone.now()
        Post.objects.create(
            title="خبر اليوم",
            link="https://sanaanet.net/p/1",
            published_at=now - timedelta(hours=2),
            source=self.source,
            voting_result=4,
            state=Post.State.APPROVED,
        )
        Post.objects.create(
            title="خبر قبل أسبوعين",
            link="https://sanaanet.net/p/2",
            published_at=now - timedelta(days=14),
            source=self.source,
            voting_result=2,
            state=Post.State.APPROVED,
        )
        SourceLog.objects.create(source=self.source, state="Error", posts_count=0)
        latest = SourceLog.objects.create(source=self.source, state="Success", posts_count=3)

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("sources:manage_list"))
        self.assertEqual(response.status_code, 200)

        sources = response.context["sources"]
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].total_posts, 2)

        metrics = response.context["source_metrics"][self.source.id]
        self.assertEqual(metrics["daily_frequency"], 1)
        self.assertEqual(metrics["weekly_frequency"], 1)
        self.assertEqual(metrics["weekly_avg_votes"], 4.0)
        self.assertEqual(metrics["monthly_avg_votes"], 3.0)
        self.assertEqual(response.context["latest_logs"][self.source.id].id, latest.id)

    def test_moderate_approve_activates_source_and_avoids_duplicate_email(self):
        self.client.force_login(self.staff_user)
        url = reverse("sources:manage_moderate", args=[self.source.id])

        # Pending page shows pending badge and approve button
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "بانتظار المراجعة")
        self.assertContains(resp_get, "قبول وتفعيل المصدر")

        # First approval activates source, sets state=VALID, sends 1 email
        resp_post = self.client.post(url, {"action": "approve"})
        self.assertRedirects(resp_post, reverse("sources:manage_list"))
        self.source.refresh_from_db()
        self.assertEqual(self.source.approve_state, Source.ApproveState.APPROVED)
        self.assertEqual(self.source.state, Source.State.VALID)
        self.assertEqual(len(mail.outbox), 1)

        # Re-opening moderation page reflects approved state (not hardcoded pending)
        resp_after = self.client.get(url)
        self.assertContains(resp_after, "مقبول ومفعل")
        self.assertNotContains(resp_after, "بانتظار المراجعة")

        # Second identical approval does NOT send duplicate email
        self.client.post(url, {"action": "approve"})
        self.assertEqual(len(mail.outbox), 1)

    def test_service_worker_bypasses_cross_origin_and_manage_routes(self):
        response = self.client.get("/sw.js")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("parsedUrl.origin !== self.location.origin", content)
        self.assertIn("/sources/manage/", content)
        self.assertIn("Response.error()", content)
