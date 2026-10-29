import os
import sys
import re
import ssl
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone as dt_tz
import feedparser
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.utils import timezone
from apps.sources.models import Source
from apps.posts.models import Post

# إعداد متصفح وتجاوز أخطاء شهادات SSL للمواقع الإخبارية ذات الشهادات منتهية الصلاحية
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

COMMON_FEED_PATHS = [
    '/feed', '/feed/', '/rss', '/rss/', '/rss.xml', '/?feed=rss2', 
    '/feed.xml', '/index.xml', '/feeds/posts/default'
]

def check_url_alive(url, timeout=7):
    """التحقق مما إذا كان الموقع يستجيب ويعمل."""
    if not url:
        return False, None
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            if resp.status < 400:
                html = resp.read().decode('utf-8', errors='ignore')
                return True, html
    except Exception:
        # تجربة http إذا فشل https
        if url.startswith('https://'):
            try:
                http_url = 'http://' + url[8:]
                req = urllib.request.Request(http_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    if resp.status < 400:
                        html = resp.read().decode('utf-8', errors='ignore')
                        return True, html
            except Exception:
                pass
    return False, None

def find_feed_links(html, base_url):
    """استخراج روابط RSS من كود الصفحة دون الحاجة لـ bs4."""
    found = []
    if not html:
        return found
    # البحث عن وسوم <link rel="alternate" ...>
    tags = re.findall(r'<link\b[^>]*>', html, re.IGNORECASE)
    for tag in tags:
        if re.search(r'type=["\'](?:application/(?:rss|atom)\+xml|text/xml)["\']', tag, re.I):
            m = re.search(r'href=["\']([^"\']+)["\']', tag, re.I)
            if m:
                feed_url = urllib.parse.urljoin(base_url, m.group(1).strip())
                if feed_url not in found:
                    found.append(feed_url)
    return found

def test_feed_and_activity(feed_url, cutoff_date):
    """اختبار صلاحية التغذية والتأكد من وجود مقال منشور خلال آخر 30 يوماً."""
    try:
        req = urllib.request.Request(feed_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=7, context=ctx) as resp:
            content = resp.read()
        
        parsed = feedparser.parse(content)
        if parsed.entries and len(parsed.entries) > 0:
            newest = parsed.entries[0]
            published_parsed = getattr(newest, 'published_parsed', None) or getattr(newest, 'updated_parsed', None)
            if published_parsed:
                entry_date = datetime(*published_parsed[:6], tzinfo=dt_tz.utc)
                if entry_date >= cutoff_date:
                    return True, True, entry_date # Valid feed + Active in last month
                else:
                    return True, False, entry_date # Valid feed + Old content
            return True, True, None # Feed works but date not parsed
    except Exception:
        pass
    return False, False, None

def check_html_has_recent_activity(html, cutoff_date):
    """فحص كود الصفحة الرئيسية للتأكد من وجود تواريخ حديثة لآخر شهر."""
    if not html:
        return False
    # فحص السنة والشهر الحاليين
    current_year = str(cutoff_date.year)
    recent_patterns = [
        rf'{current_year}-10', rf'{current_year}-09',
        r'أكتوبر\s*' + current_year, r'سبتمبر\s*' + current_year,
        r'منذ\s*(?:ساعة|ساعتين|ساعات|يوم|يومين|أيام|أسبوع)',
        r'(?:hours?|days?|minutes?)\s*ago'
    ]
    for pattern in recent_patterns:
        if re.search(pattern, html, re.I):
            return True
    return False

def run_audit(dry_run=True, mode='soft', limit=None):
    now = timezone.now()
    cutoff_date = now - timedelta(days=30)
    
    # فلترة المصادر المعطلة
    sources_qs = Source.objects.filter(state='invalid').order_by('id')
    if limit:
        sources_qs = sources_qs[:limit]

    total = sources_qs.count()
    print(f"\n=======================================================")
    print(f" 🚀 بدء فحص مصادر الأخبار المعطلة (إجمالي: {total})")
    print(f" الوضع: {'معاينة فقط (Dry-Run)' if dry_run else f'تطبيق فعلي ({mode}-delete)'}")
    print(f" تاريخ الحد الأدنى للنشاط: {cutoff_date.strftime('%Y-%m-%d')}")
    print(f"=======================================================\n")

    stats = {'dead': 0, 'inactive': 0, 'recovered': 0, 'kept': 0}

    for idx, s in enumerate(sources_qs, 1):
        target_site = s.website or s.link
        posts_count = Post.objects.filter(source=s).count()
        print(f"[{idx}/{total}] المصدر: {s.name} (ID: {s.id} | مقالاته: {posts_count})")
        print(f"   الرابط الحالي: {s.link}")

        # 1. Alive Check
        alive, html = check_url_alive(target_site)
        if not alive and s.website and s.website != s.link:
            # تجربة رابط التغذية في حال كان رابط الموقع مختلفاً
            alive, html = check_url_alive(s.link)

        if not alive:
            print(f"   ❌ الموقع ميت تماماً ولا يستجيب (Dead Domain)")
            stats['dead'] += 1
            if not dry_run:
                if mode == 'hard':
                    s.delete()
                    print(f"      🗑️ تم حذفه نهائياً من قاعدة البيانات مع مقالاته.")
                else:
                    s.deleted_at = now
                    s.state = 'invalid'
                    s.save(update_fields=['deleted_at', 'state'])
                    print(f"      🔒 تم تعطيله وأرشفته (Soft Delete).")
            continue

        print(f"   🌐 الموقع حي ويستجيب بنجاح.")

        # 2. Activity Check & RSS Discovery
        # تجميع الروابط المحتملة للتغذية
        candidate_feeds = find_feed_links(html, target_site)
        for path in COMMON_FEED_PATHS:
            full_path = urllib.parse.urljoin(target_site, path)
            if full_path not in candidate_feeds:
                candidate_feeds.append(full_path)

        # تجربة رابط الـ RSS الحالي أولاً
        if s.link not in candidate_feeds:
            candidate_feeds.insert(0, s.link)

        found_working_feed = None
        has_published_recently = False

        for feed_candidate in candidate_feeds[:6]:
            is_valid_feed, is_recent, entry_dt = test_feed_and_activity(feed_candidate, cutoff_date)
            if is_valid_feed:
                if is_recent:
                    found_working_feed = feed_candidate
                    has_published_recently = True
                    break
                else:
                    # تغذية تعمل لكن محتواها قديم
                    pass

        # إذا لم يتم التأكد من النشاط عبر الـ RSS، نفحص الصفحة الرئيسية
        if not has_published_recently:
            has_published_recently = check_html_has_recent_activity(html, cutoff_date)

        if not has_published_recently:
            print(f"   ⚠️ الموقع حي لكنه متوقف عن نشر الأخبار منذ أكثر من شهر (Inactive)")
            stats['inactive'] += 1
            if not dry_run:
                if mode == 'hard':
                    s.delete()
                    print(f"      🗑️ تم حذفه نهائياً لعدم النشاط.")
                else:
                    s.deleted_at = now
                    s.save(update_fields=['deleted_at'])
                    print(f"      🔒 تم تعطيله لعدم النشاط (Soft Delete).")
            continue

        # الموقع نشط
        if found_working_feed and found_working_feed != s.link:
            print(f"   ✨ تم العثور على رابط RSS بديل يعمل: {found_working_feed}")
            stats['recovered'] += 1
            if not dry_run:
                s.link = found_working_feed
                s.state = 'valid'
                s.save(update_fields=['link', 'state'])
                print(f"      ✅ تم تحديث الرابط في الـ DB وإعادة حالته إلى Valid!")
        else:
            print(f"   ℹ️ الموقع حي ونشط ولكن لم يتم العثور على رابط RSS بديل -> الإبقاء عليه كما هو.")
            stats['kept'] += 1

    print(f"\n=======================================================")
    print(f" 📊 ملخص نتائج الفحص:")
    print(f" • مواقع ميتة تماماً (مؤهلة للحذف)     : {stats['dead']}")
    print(f" • مواقع متوقفة عن النشر (مؤهلة للحذف): {stats['inactive']}")
    print(f" • مصادر تم اكتشاف RSS بديل وتحديثها  : {stats['recovered']}")
    print(f" • مصادر نشطة لم نجد لها RSS وبقيت    : {stats['kept']}")
    print(f"=======================================================\n")

if __name__ == '__main__':
    args = sys.argv[1:]
    is_dry = '--apply' not in args
    delete_mode = 'hard' if '--hard' in args else 'soft'
    limit_val = 10 if '--sample' in args else None

    run_audit(dry_run=is_dry, mode=delete_mode, limit=limit_val)
