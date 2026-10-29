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
        self.assertIn("أبرز الأخبار والتغطيات المجمعة", content)
        self.assertIn("اختيارات القراء", content)
        self.assertIn("آخر الأخبار (مباشر)", content)
        self.assertIn("مقالات وآراء", content)
        self.assertIn("أسعار الصرف في اليمن", content)
        self.assertIn("حالة الطقس في اليمن", content)
        self.assertIn("دليل المواقع الأكثر متابعة", content)

    def test_clusterer_groups_similar_arabic_headlines_and_sorts_sections(self):
        from apps.posts.services.clusterer import PostClusterer
        source2 = Source.objects.create(
            name="عدن الغد",
            link="https://adengad.net/rss",
            website="https://adengad.net",
            state=Source.State.VALID,
            approve_state=Source.ApproveState.APPROVED,
        )
        p_a = Post.objects.create(
            title="مجلس القيادة الرئاسي يعقد اجتماعا طارئا في العاصمة عدن لمناقشة الأوضاع الاقتصادية",
            description="عقد مجلس القيادة الرئاسي اجتماعا في عدن",
            link="https://almasdaronline.com/post/101",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
            post_views_count=50,
        )
        p_b = Post.objects.create(
            title="القيادة الرئاسي يعقد اجتماعا استثنائيا في عدن لبحث الأوضاع الاقتصادية والخدمية",
            description="تفاصيل اجتماع مجلس القيادة في عدن",
            link="https://adengad.net/post/102",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=source2,
            post_views_count=60,
        )
        clusterer = PostClusterer()
        clusterer.clusterize_recent_posts(unclustered_hours=24, force_recluster=True)
        p_a.refresh_from_db()
        p_b.refresh_from_db()
        self.assertIsNotNone(p_a.topic_id)
        self.assertEqual(p_a.topic_id, p_b.topic_id)
        self.assertGreaterEqual(p_a.topic.topic_size, 2)

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
        self.assertEqual(min(response.context["archive_years"]), 2013)

        response_empty = self.client.get(
            f"{reverse('archive')}?year=2013&month=1",
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

    def test_intelligent_categorizer_prevents_false_sports_tagging(self):
        from apps.posts.services.categorizer import classify_post_categories
        cat_sports = Category.objects.create(name="رياضة")
        cat_local = Category.objects.create(name="محلي")
        cache.delete("portal_category_name_map_v1")

        # 1. Real sports article -> gets رياضة
        sports_ids = classify_post_categories(
            title="منتخب اليمن للناشئين يتأهل إلى نصف نهائي بطولة كأس الخليج لكرة القدم",
            description="فاز المنتخب الوطني في المباراة",
        )
        self.assertIn(cat_sports.id, sports_ids)

        # 2. Military/local news -> gets محلي and NEVER gets رياضة
        military_ids = classify_post_categories(
            title="القوات المسلحة اليمنية: تنفيذ 982 عملية عسكرية في تعز ومأرب",
            description="تفاصيل العمليات العسكرية",
            rss_tags=["رياضة"],  # Even if a broken feed tag says رياضة, negative constraint blocks it
        )
        self.assertIn(cat_local.id, military_ids)
        self.assertNotIn(cat_sports.id, military_ids)

