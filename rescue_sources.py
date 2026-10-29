import os, sys, re, ssl, urllib.request, urllib.parse, feedparser, django
from datetime import datetime, timedelta, timezone as dt_tz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.utils import timezone
from apps.sources.models import Source

ctx = ssl._create_unverified_context()
HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36'}
PATHS = ['/rss.php', '/feed/', '/feed', '/rss/', '/rss', '/rss.xml', '/?feed=rss2', '/news_rss.php', '/rsslastnews.php', '/.mrss/alhadath.xml', '/ar/rss.xml']
SQUAT_RE = re.compile(r'\b(casino|gambling|betting|poker|roulette)\b|كازينو|مراهنات|لعب القمار|expireddomains|sedo\.com|dan\.com|hugedomains|domain is for sale|هذا النطاق للبيع', re.I)
NEWS_WORDS = ['أخبار', 'اخبار', 'عاجل', 'اليمن', 'سياسة', 'اقتصاد', 'تقارير', 'news', 'yemen']

def fetch(u):
    try:
        req = urllib.request.Request(u, headers=HDR)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            return r.status, r.geturl(), r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        if e.code in [401, 403]: return e.code, u, ""
    except Exception:
        pass
    return None, None, ""

def test_feed(u, cutoff):
    try:
        req = urllib.request.Request(u, headers=HDR)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            p = feedparser.parse(r.read())
        if p.entries and len(p.entries) > 0:
            dt = None
            for e in p.entries[:5]:
                t = getattr(e, 'published_parsed', None) or getattr(e, 'updated_parsed', None)
                if t:
                    try:
                        d = datetime(*t[:6], tzinfo=dt_tz.utc)
                        if not dt or d > dt: dt = d
                    except Exception: pass
            return True, (dt and dt >= cutoff), dt, len(p.entries)
    except Exception: pass
    return False, False, None, 0

def get_domain_variants(s):
    urls = []
    for raw in [s.website, s.link]:
        if not raw: continue
        p = urllib.parse.urlparse(raw if '://' in raw else 'http://' + raw)
        h = p.netloc.split(':')[0].lower().replace('www.', '')
        if h and '.' in h:
            for proto in ['https://', 'http://', 'https://www.', 'http://www.']:
                u = proto + h
                if u not in urls: urls.append(u)
    return urls

def find_feed(fin, html, cutoff):
    cands = []
    if html:
        hrefs = re.findall(r'href="([^"]+)"', html, re.I) + re.findall(r"href='([^']+)'", html, re.I)
        for h in hrefs:
            if any(k in h.lower() for k in ['rss', 'feed', 'atom']) and not any(x in h.lower() for x in ['facebook', 'twitter', 'instagram']):
                cands.append(urllib.parse.urljoin(fin, h.strip()))
    for p in PATHS: cands.append(urllib.parse.urljoin(fin, p))
    seen = set()
    uniq = [x for x in cands if not (x in seen or seen.add(x))]
    best = None
    for u in uniq[:14]:
        ok, recent, dt, count = test_feed(u, cutoff)
        if ok:
            if recent: return u, dt, count
            if not best: best = (u, dt, count)
    return best if best else (None, None, 0)

def run():
    apply = '--apply' in sys.argv
    limit = 10 if '--sample' in sys.argv else None
    cutoff = timezone.now() - timedelta(days=60)
    qs = Source.objects.filter(state='invalid').order_by('id')
    if limit: qs = qs[:limit]
    print(f"=== Auditing {qs.count()} Sources | Apply Mode: {apply} ===")
    rec, alive, dead = 0, 0, 0
    for s in qs:
        print(f"\n[{s.id}] {s.name} ({s.link[:35]}...)")
        root, fin, html = None, None, ""
        for u in get_domain_variants(s):
            st, final_url, page_html = fetch(u)
            if st and st < 400:
                root, fin, html = u, final_url, page_html
                break
            elif st in [401, 403]:
                root, fin, html = u, u, ""
                break

        if not root:
            print(f"  ❌ Domain Unreachable -> Eligible for deletion")
            dead += 1
            continue

        feed, dt, count = find_feed(fin, html, cutoff)
        if feed:
            d_str = dt.strftime('%Y-%m-%d') if dt else 'unknown'
            print(f"  ✨ Working RSS ({count} articles | {d_str}): {feed}")
            rec += 1
            if apply:
                s.link, s.website, s.state, s.deleted_at = feed, fin, 'valid', None
                s.save(update_fields=['link', 'website', 'state', 'deleted_at'])
                print("     ✅ Saved to DB as Valid")
            continue

        blob = (fin + " " + html[:8000]).lower()
        if SQUAT_RE.search(blob):
            print(f"  ❌ SQUATTED/PARKED ({fin}) -> Eligible for deletion")
            dead += 1
            continue

        matches = sum(1 for w in NEWS_WORDS if w in blob)
        if s.name.lower() not in blob and matches < 2 and len(html) > 500:
            print(f"  ❌ NOT_NEWS ({fin}) -> Eligible for deletion")
            dead += 1
            continue

        print(f"  🌐 Alive News Site ({fin}) - Kept in DB")
        alive += 1

    print(f"\nDone: {rec} recovered | {alive} alive | {dead} dead/squatted\n")

if __name__ == '__main__':
    run()
