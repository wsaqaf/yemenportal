from django.test import TestCase
from apps.sources.classifier import classify_source_scope
from apps.sources.forms import SourceSuggestionForm


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
