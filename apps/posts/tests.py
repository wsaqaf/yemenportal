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
        self.assertIn("الأكثر تفاعلاً", content)
        self.assertIn("إحصائيات الرصد والأرشفة", content)
        self.assertIn("مقالات وآراء", content)
        self.assertIn("أسعار الصرف في اليمن", content)
        self.assertIn("حالة الطقس في اليمن", content)
        self.assertIn("دليل المواقع الأكثر متابعة", content)
        self.assertIn(f"vote-controls-{self.post1.id}", content)
        self.assertIn("أؤيد الخبر", content)

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

    def test_clusterer_prevents_false_grouping_and_chaining(self):
        """Verifies that generic boilerplate (e.g. 'داخل سجون الحوثيين') does NOT cluster unrelated events."""
        from apps.posts.services.clusterer import PostClusterer
        source2 = Source.objects.create(
            name="عدن تايم",
            link="https://aden-tm.net/rss",
            website="https://aden-tm.net",
            state=Source.State.VALID,
            approve_state=Source.ApproveState.APPROVED,
        )
        source3 = Source.objects.create(
            name="الوطن العدنية",
            link="https://alwatan.net/rss",
            website="https://alwatan.net",
            state=Source.State.VALID,
            approve_state=Source.ApproveState.APPROVED,
        )
        p_un1 = Post.objects.create(
            title="وفاة موظف أممي داخل أحد معتقلات الحوثيين بعد عامين من اعتقاله في صنعاء",
            description="تفاصيل وفاة موظف الأمم المتحدة",
            link="https://almasdaronline.com/post/201",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
        )
        p_un2 = Post.objects.create(
            title="مفوضية حقوق الإنسان تدين وفاة موظف أممي في سجون الحوثيين وتطالب بتحقيق مستقل",
            description="بيان مفوضية حقوق الإنسان",
            link="https://aden-tm.net/post/202",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=source2,
        )
        p_boy = Post.objects.create(
            title="مقتل فتى في ظروف غامضة داخل سجون الحوثيين عقب فراره من جبهات تعز",
            description="مقتل فتى داخل قسم شرطة",
            link="https://alwatan.net/post/203",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=source3,
        )

        clusterer = PostClusterer()
        clusterer.clusterize_recent_posts(unclustered_hours=24, force_recluster=True)
        p_un1.refresh_from_db()
        p_un2.refresh_from_db()
        p_boy.refresh_from_db()

        # The two UN employee posts must be clustered together
        self.assertIsNotNone(p_un1.topic_id)
        self.assertEqual(p_un1.topic_id, p_un2.topic_id)

        # The unrelated boy post must NOT be grouped into the UN topic
        self.assertNotEqual(p_boy.topic_id, p_un1.topic_id)

    def test_clusterer_does_not_group_unrelated_articles_sharing_calendar_dates(self):
        """Verifies that commodity/bulletin articles sharing identical calendar dates ('اليوم الأحد 1 نوفمبر 2026') do NOT cluster."""
        from apps.posts.services.clusterer import PostClusterer
        source2 = Source.objects.create(
            name="المشهد اليمني",
            link="https://almashhad.net/rss",
            website="https://almashhad.net",
            state=Source.State.VALID,
            approve_state=Source.ApproveState.APPROVED,
        )
        p_poultry = Post.objects.create(
            title="أسعار الدواجن اليوم الأحد 1 نوفمبر 2026",
            description="نشرة أسعار الدواجن والبيض اليوم الأحد 1 نوفمبر 2026",
            link="https://almasdaronline.com/post/301",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=self.source,
        )
        p_gold = Post.objects.create(
            title="أسعار الذهب اليوم الأحد 1 نوفمبر 2026",
            description="تعرف على أسعار الذهب اليوم الأحد 1 نوفمبر 2026",
            link="https://almashhad.net/post/302",
            published_at=timezone.now(),
            state=Post.State.APPROVED,
            source=source2,
        )

        clusterer = PostClusterer()
        clusterer.clusterize_recent_posts(unclustered_hours=24, force_recluster=True)
        p_poultry.refresh_from_db()
        p_gold.refresh_from_db()

        # Poultry prices and Gold prices must NEVER be clustered together
        if p_poultry.topic_id and p_gold.topic_id:
            self.assertNotEqual(p_poultry.topic_id, p_gold.topic_id)

    def test_foreign_domestic_news_blocked_from_top_news(self):
        """Verifies foreign domestic news is barred from Top News, while major regional events qualify."""
        from apps.posts.services.portal_services import (
            is_foreign_domestic_story,
            is_eligible_for_top_news,
            is_yemen_relevant,
            is_major_regional_event,
        )

        # 1. Foreign domestic commodity / currency article -> BLOCKED
        p_egypt_dollar = Post(
            title="أسعار الدولار اليوم الأحد 1 نوفمبر 2026",
            description="تباينت أسعار الدولار مقابل الجنيه المصري في البنوك المصرية وسجل في البنك المركزي المصري 55 جنيها",
            source=self.source,
        )
        self.assertTrue(is_foreign_domestic_story(p_egypt_dollar.title, p_egypt_dollar.description))
        self.assertFalse(is_eligible_for_top_news(p_egypt_dollar))
        self.assertFalse(is_yemen_relevant(p_egypt_dollar))

        # 2. Major regional/international breaking event -> ALLOWED
        p_gaza = Post(
            title="عاجل: غارات إسرائيلية عنيفة تستهدف مخيم جباليا شمال قطاع غزة",
            description="قصف مكثف لقوات الاحتلال الإسرائيلي على شمال غزة وسقوط شهداء وجرحى",
            source=self.source,
        )
        self.assertFalse(is_foreign_domestic_story(p_gaza.title, p_gaza.description))
        self.assertTrue(is_major_regional_event(p_gaza))
        self.assertTrue(is_eligible_for_top_news(p_gaza))

        # 3. Genuine Yemen political/conflict news -> ALLOWED
        p_yemen = Post(
            title="رئيس مجلس القيادة الرئاسي رشاد العليمي يصل العاصمة عدن",
            description="وصل الدكتور رشاد العليمي رئيس مجلس القيادة الرئاسي إلى العاصمة المؤقتة عدن",
            source=self.source,
        )
        self.assertFalse(is_foreign_domestic_story(p_yemen.title, p_yemen.description))
        self.assertTrue(is_eligible_for_top_news(p_yemen))
        self.assertTrue(is_yemen_relevant(p_yemen))

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

    def test_arabic_sources_pluralization(self):
        from apps.posts.templatetags.arabic_time import arabic_sources
        self.assertEqual(arabic_sources(1), "مصدر")
        self.assertEqual(arabic_sources(2), "مصدرين")
        self.assertEqual(arabic_sources(3), "3 مصادر")
        self.assertEqual(arabic_sources(10), "10 مصادر")
        self.assertEqual(arabic_sources(11), "11 مصدر")
        self.assertEqual(arabic_sources(12), "12 مصدر")
        self.assertEqual(arabic_sources(39), "39 مصدر")

    def test_report_iframe_blocked_view_disables_source_iframe(self):
        """Verifies reporting an iframe as blocked disables iframe_flag for that source."""
        self.assertTrue(self.source.iframe_flag)
        res = self.client.post(reverse('posts:report_iframe_blocked', kwargs={'pk': self.post1.pk}))
        self.assertEqual(res.status_code, 200)
        self.source.refresh_from_db()
        self.assertFalse(self.source.iframe_flag)

    def test_pwa_endpoints(self):
        # 1. Manifest
        manifest_res = self.client.get("/manifest.json")
        self.assertEqual(manifest_res.status_code, 200)
        self.assertIn("application/manifest+json", manifest_res["Content-Type"])
        data = manifest_res.json()
        self.assertEqual(data.get("short_name"), "يمن بورتال")
        self.assertEqual(data.get("display"), "standalone")

        # 2. Service Worker
        sw_res = self.client.get("/sw.js")
        self.assertEqual(sw_res.status_code, 200)
        self.assertIn("application/javascript", sw_res["Content-Type"])
        self.assertEqual(sw_res["Service-Worker-Allowed"], "/")
        self.assertIn("yp-pwa", sw_res.content.decode("utf-8"))

        # 3. Offline fallback page
        offline_res = self.client.get("/offline/")
        self.assertEqual(offline_res.status_code, 200)
        self.assertIn("أنت تتصفح دون اتصال", offline_res.content.decode("utf-8"))

    def test_record_share_view(self):
        """Test recording shares increments shares_count and enforces rate-limiting."""
        self.assertEqual(self.post1.shares_count, 0)
        url = reverse('posts:record_share', kwargs={'pk': self.post1.pk})

        # 1. Successful record
        res = self.client.post(url, data='{"platform":"whatsapp"}', content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('status'), 'ok')
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.shares_count, 1)

        # 2. Cooldown deduplication within 5 minutes
        res2 = self.client.post(url, data='{"platform":"whatsapp"}', content_type='application/json')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json().get('status'), 'already_recorded')
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.shares_count, 1)

        # 3. Unknown post returns 404
        res404 = self.client.post(reverse('posts:record_share', kwargs={'pk': 999999}))
        self.assertEqual(res404.status_code, 404)

    def test_homepage_widgets_contain_most_shared_and_top_voted(self):
        """Verifies get_homepage_portal_widgets includes most_shared_posts and top_voted_posts."""
        from apps.posts.services.portal_services import get_homepage_portal_widgets
        cache.clear()
        self.post1.shares_count = 15
        self.post1.save(update_fields=['shares_count'])
        self.post1.voting_result = 8
        self.post1.save(update_fields=['voting_result'])

        widgets = get_homepage_portal_widgets()
        self.assertIn("most_shared_posts", widgets)
        self.assertIn("top_voted_posts", widgets)
        self.assertTrue(len(widgets["most_shared_posts"]) > 0)
        self.assertTrue(len(widgets["top_voted_posts"]) > 0)
        self.assertEqual(widgets["most_shared_posts"][0].id, self.post1.id)
        self.assertEqual(widgets["top_voted_posts"][0].id, self.post1.id)

    def test_vote_view_compact_and_toggle(self):
        """Test voting as authenticated user with compact and hide_report params."""
        from apps.users.models import User
        user = User(email="voter@example.com")
        user.set_password("password123")
        user.save()
        self.client.force_login(user)

        url = reverse('posts:vote', kwargs={'pk': self.post1.pk})
        res = self.client.post(url, data={'value': '1', 'compact': '1', 'hide_report': '1'})
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')
        self.assertIn('w-3 h-3', content)
        self.assertNotIn('triggerReportModal', content)

        self.post1.refresh_from_db()
        self.assertEqual(self.post1.voting_result, 1)

