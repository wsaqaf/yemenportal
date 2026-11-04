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
        self.source1 = Source.objects.create(name="المصدر الأول", website="https://s1.ye", link="https://s1.ye/rss")
        self.source2 = Source.objects.create(name="المصدر الثاني", website="https://s2.ye", link="https://s2.ye/rss")
        self.source3 = Source.objects.create(name="المصدر الثالث", website="https://s3.ye", link="https://s3.ye/rss")

        self.post1 = Post.objects.create(
            title="خبر عاجل ومهم حول التطورات",
            link="https://s1.ye/news/1",
            published_at=timezone.now(),
            source=self.source1,
            state=Post.State.APPROVED,
        )
        self.post2 = Post.objects.create(
            title="تطورات عاجلة في نفس الحدث",
            link="https://s2.ye/news/2",
            published_at=timezone.now(),
            source=self.source2,
            state=Post.State.APPROVED,
        )
        self.post3 = Post.objects.create(
            title="تغطية موسعة لنفس الحدث",
            link="https://s3.ye/news/3",
            published_at=timezone.now(),
            source=self.source3,
            state=Post.State.APPROVED,
        )

        self.topic = Topic.objects.create(main_post=self.post1, topic_size=3)
        self.post1.topic = self.topic
        self.post1.save()
        self.post2.topic = self.topic
        self.post2.save()
        self.post3.topic = self.topic
        self.post3.save()

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_publish_hot_cluster_success(self, mock_send):
        mock_send.return_value = {'ok': True, 'result': {'message_id': 123}}

        results = publish_next_hot_cluster(min_sources=3, max_per_run=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'published')
        self.assertEqual(results[0]['topic_id'], self.topic.id)

        # Check PublishedChannelPost record created
        pub = PublishedChannelPost.objects.get(topic=self.topic)
        self.assertEqual(pub.channel, PublishedChannelPost.Channel.TELEGRAM)
        self.assertEqual(pub.post_type, PublishedChannelPost.PostType.HOT_CLUSTER)
        self.assertIn("utm_source=telegram", pub.message_text)
        self.assertIn("3 مصادر إخبارية", pub.message_text)

        # Should not publish the same topic again
        results_again = publish_next_hot_cluster(min_sources=3, max_per_run=1)
        self.assertEqual(len(results_again), 0)

    @patch('apps.growth.services.telegram_service.send_telegram_message')
    def test_publish_morning_exchange_rates(self, mock_send):
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
