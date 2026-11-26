from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from apps.posts.models import Topic, Post
from apps.sources.models import Source
from apps.growth.models import PublishedChannelPost
from apps.growth.services.telegram_service import (
    publish_morning_exchange_rates,
    publish_next_hot_cluster,
)


class TelegramGrowthTests(TestCase):
    def setUp(self):
        self.sources = [
            Source.objects.create(
                name=f"المصدر اليمني {i}",
                website=f"https://s{i}.ye",
                link=f"https://s{i}.ye/rss",
            )
            for i in range(1, 10)
        ]

    def _create_cluster(self, title, num_sources, slug="news", repeat_first_source=0):
        posts = []
        for idx in range(num_sources):
            src = self.sources[idx]
            posts.append(
                Post.objects.create(
                    title=title if idx == 0 else f"تغطية {idx} - {title}",
                    link=f"https://s{idx+1}.ye/{slug}/{idx}",
                    published_at=timezone.now(),
                    source=src,
                    state=Post.State.APPROVED,
                )
            )
        for extra in range(repeat_first_source):
            posts.append(
                Post.objects.create(
                    title=f"مكرر {extra} - {title}",
                    link=f"https://s1.ye/{slug}/extra-{extra}",
                    published_at=timezone.now(),
                    source=self.sources[0],
                    state=Post.State.APPROVED,
                )
            )
        topic = Topic.objects.create(main_post=posts[0], topic_size=len(posts))
        Post.objects.filter(id__in=[p.id for p in posts]).update(topic=topic)
        return topic

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_small_non_urgent_cluster_is_skipped(self, mock_send):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 100}}
        # 4 distinct sources, non-urgent headline -> below major threshold (6) and not urgent
        self._create_cluster("اجتماع رسمي لمناقشة خطة الخدمات في عدن", num_sources=4, slug="small")
        results = publish_next_hot_cluster()
        self.assertEqual(results, [])
        mock_send.assert_not_called()

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_duplicate_posts_from_few_sources_do_not_bypass_distinct_threshold(self, mock_send):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 101}}
        # topic_size=8, but only 3 distinct sources -> must be skipped (urgent requires >= 4 distinct)
        self._create_cluster("عاجل: قصف في تعز", num_sources=3, slug="dups", repeat_first_source=5)
        results = publish_next_hot_cluster()
        self.assertEqual(results, [])
        mock_send.assert_not_called()

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_urgent_cluster_publishes_at_4_distinct_sources(self, mock_send):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 123}}
        topic = self._create_cluster(
            "عاجل: غارات جوية تستهدف مواقع عسكرية في الحديدة وصنعاء",
            num_sources=4,
            slug="urgent4",
        )

        results = publish_next_hot_cluster()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'published')
        self.assertEqual(results[0]['topic_id'], topic.id)
        self.assertTrue(results[0]['urgent'])

        pub = PublishedChannelPost.objects.get(topic=topic)
        self.assertEqual(pub.channel, PublishedChannelPost.Channel.TELEGRAM)
        self.assertEqual(pub.post_type, PublishedChannelPost.PostType.BREAKING)
        self.assertIn("utm_source=telegram", pub.message_text)
        self.assertIn("المصادر (4)", pub.message_text)
        self.assertIn(f"<a href=\"https://yemenportal.net/posts/topic/{topic.id}/", pub.message_text)

        # Should not publish the same topic again
        results_again = publish_next_hot_cluster(respect_limits=False)
        self.assertEqual(len(results_again), 0)

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_major_cluster_publishes_at_6_distinct_sources_and_respects_cooldown(self, mock_send):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 125}}
        topic1 = self._create_cluster(
            "البنك المركزي في عدن يعلن إجراءات جديدة لضبط سوق الصرافة في اليمن",
            num_sources=6,
            slug="major1",
        )
        topic2 = self._create_cluster(
            "مجلس القيادة الرئاسي اليمني يعقد اجتماعاً موسعاً لمناقشة الملف الاقتصادي",
            num_sources=6,
            slug="major2",
        )

        # First major cluster publishes
        res1 = publish_next_hot_cluster(max_per_run=1)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0]['topic_id'], topic1.id)

        # Second major cluster immediately blocked by cooldown
        res2 = publish_next_hot_cluster(max_per_run=1)
        self.assertEqual(res2, [])

        # Simulate 20 minutes passing: non-urgent still blocked (<45m), urgent allowed (>=15m)
        PublishedChannelPost.objects.filter(topic=topic1).update(
            created_at=timezone.now() - timedelta(minutes=20)
        )
        self.assertEqual(publish_next_hot_cluster(max_per_run=1), [])

        urgent_topic = self._create_cluster(
            "عاجل: اعتراض صاروخ باليستي حوثي فوق مأرب",
            num_sources=4,
            slug="urgent_after_20m",
        )
        res3 = publish_next_hot_cluster(max_per_run=1)
        self.assertEqual(len(res3), 1)
        self.assertEqual(res3[0]['topic_id'], urgent_topic.id)

        # Simulate daily cap reached: non-urgent major cluster stays blocked
        PublishedChannelPost.objects.filter(topic=urgent_topic).update(
            created_at=timezone.now() - timedelta(minutes=60)
        )
        res_capped = publish_next_hot_cluster(max_per_run=1, max_daily_posts=2)
        self.assertEqual(res_capped, [])
        self.assertEqual(topic2.channel_publications.count(), 0)

        # Major breaking urgent story (>= 6 distinct sources) still breaks through the daily cap
        breaking_major = self._create_cluster(
            "عاجل: غارات جوية مكثفة تستهدف مواقع عسكرية في صنعاء",
            num_sources=6,
            slug="breaking_major_bypass",
        )
        res_bypass = publish_next_hot_cluster(max_per_run=1, max_daily_posts=2)
        self.assertEqual(len(res_bypass), 1)
        self.assertEqual(res_bypass[0]['topic_id'], breaking_major.id)

    @patch('apps.posts.services.portal_services.update_exchange_rates_from_kuraimi', return_value=0)
    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_publish_morning_exchange_rates(self, mock_send, mock_kuraimi):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 124}}

        res = publish_morning_exchange_rates(force=True)
        self.assertEqual(res['status'], 'published')

        pub = PublishedChannelPost.objects.filter(
            post_type=PublishedChannelPost.PostType.EXCHANGE_RATES
        ).first()
        self.assertIsNotNone(pub)
        self.assertIn("أسعار الصرف في اليمن", pub.message_text)
        self.assertIn("صنعاء", pub.message_text)
        self.assertIn("عدن", pub.message_text)
        self.assertIn("بنك الكريمي", pub.message_text)


class BotProtectionAndPerformanceTests(TestCase):
    def test_robots_txt_view(self):
        resp = self.client.get('/robots.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/plain; charset=utf-8')
        content = resp.content.decode('utf-8')
        self.assertIn("User-agent: Amazonbot", content)
        self.assertIn("User-agent: Baiduspider", content)
        self.assertIn("Disallow: /*?*sources=", content)

    def test_middleware_blocks_abusive_scrapers(self):
        # Baiduspider blocked
        resp = self.client.get('/', HTTP_USER_AGENT='Baiduspider/2.0 (+http://www.baidu.com/search/spider.html)')
        self.assertEqual(resp.status_code, 403)

        # Amazonbot blocked
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0 (compatible; Amazonbot/0.1)')
        self.assertEqual(resp.status_code, 403)

        # Meta AI external agent blocked
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 (compatible; meta-externalagent/1.1)')
        self.assertEqual(resp.status_code, 403)

        # Archaic spoofed Chrome/48 Chinese scraper farm blocked
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
        self.assertEqual(resp.status_code, 403)

        # Truncated fake UA blocked
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.assertEqual(resp.status_code, 403)

        # Normal browser allowed
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        self.assertEqual(resp.status_code, 200)

    def test_middleware_blocks_bot_impressions(self):
        resp = self.client.post(
            '/posts/record-impressions/',
            data='{"post_ids": [1, 2]}',
            content_type='application/json',
            HTTP_USER_AGENT='Mozilla/5.0 (compatible; SomeSearchBot/1.0)'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('status'), 'ignored')
        self.assertEqual(data.get('reason'), 'bot')

