from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from apps.sources.models import Source
from apps.posts.models import Post, Category, CurrencyRate


class PortalServicesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()
        self.source = Source.objects.create(
            name="المصدر أونلاين",
            link="https://almasdaronline.com/rss",
            website="https://almasdaronline.com",
            state=Source.State.VALID,
            approve_state=Source.ApproveState.APPROVED,
        )
        self.cat_opinion = Category.objects.create(name="آراء")
        self.cat_economy = Category.objects.create(name="اقتصاد")

        self.post1 = Post.objects.create(
            title="عاجل: تطورات جديدة في العاصمة صنعاء وعدن",
            description="تفاصيل الخبر الأول",
            link="https://almasdaronline.com/post/1",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
            image_url="https://almasdaronline.com/img1.jpg",
            post_views_count=150,
            voting_result=5,
        )
        self.post2 = Post.objects.create(
            title="أسعار الصرف اليوم في عدن وصنعاء مقابل الدولار والريال السعودي",
            description="تحديث أسعار الصرف",
            link="https://almasdaronline.com/post/2",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
            post_views_count=420,
        )
        self.post2.categories.add(self.cat_economy)

        self.post3 = Post.objects.create(
            title="مقال رأي حول مستقبل الاقتصاد اليمني",
            description="بقلم كاتب يمني",
            link="https://almasdaronline.com/post/3",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
            post_views_count=85,
        )
        self.post3.categories.add(self.cat_opinion)

    def test_homepage_renders_sahaafa_style_widgets(self):
        response = self.client.get(reverse("home"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("اختيارات القراء", content)
        self.assertIn("مقالات وآراء", content)
        self.assertIn("أسعار الصرف في اليمن", content)
        self.assertIn("حالة الطقس في اليمن", content)
        self.assertIn("دليل المواقع الأكثر متابعة", content)

    def test_most_read_page_orders_by_views(self):
        response = self.client.get(reverse("most_read") + "?window=24h", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        posts = list(response.context["posts"])
        self.assertGreaterEqual(len(posts), 2)
        self.assertEqual(posts[0].id, self.post2.id)

    def test_archive_page_filters_by_year_and_month(self):
        now = timezone.now()
        response = self.client.get(
            f"{reverse('archive')}?year={now.year}&month={now.month}&day={now.day}",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 3)

        response_empty = self.client.get(
            f"{reverse('archive')}?year=2010&month=1",
            HTTP_HOST="localhost",
        )
        self.assertEqual(response_empty.status_code, 200)
        self.assertEqual(len(response_empty.context["posts"]), 0)

    def test_currency_service_page_and_rates_seeding(self):
        response = self.client.get(reverse("currency_service"), HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CurrencyRate.objects.filter(region="aden", currency_code="USD").exists())
        self.assertTrue(CurrencyRate.objects.filter(region="sanaa", currency_code="USD").exists())
        content = response.content.decode("utf-8")
        self.assertIn("حاسبة تحويل العملات الفورية", content)
