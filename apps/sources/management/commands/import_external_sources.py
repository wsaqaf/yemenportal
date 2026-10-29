import re
import socket
import urllib3
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import feedparser

from django.core.management.base import BaseCommand
from apps.sources.models import Source

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
}

COMMON_FEED_PATHS = [
    '/feed', '/feed/', '/rss', '/rss.xml', '/?feed=rss2', '/rss.php', 
    '/feed/home.xml', '/RSS.aspx', '/rss/main', '/index.php?format=feed&type=rss'
]

IGNORE_DOMAINS = {
    'sahaafa.net', 'msader-ye.net', 'facebook.com', 'twitter.com', 'x.com',
    'youtube.com', 'telegram.me', 't.me', 'instagram.com', 'whatsapp.com',
    'google.com', 'hugedomains.com', 'cloudflare.com'
}

def check_dns(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False

def clean_arabic_title(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text or '').strip()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'(\s*[-|–]\s*(الرئيسية|الصفحة الرئيسية|الأخبار|أخبار اليمن|اليمن)).*$', '', text)
    return text.strip()

def test_feed(url: str):
    try:
        res = requests.get(url, headers=BROWSER_HEADERS, timeout=8, verify=False)
        if res.status_code == 200:
            feed = feedparser.parse(res.content)
            if len(feed.entries) > 0:
                sample = (feed.entries[0].get('title', '') + ' ' + feed.entries[0].get('summary', ''))
                has_arabic = bool(re.search(r'[\u0600-\u06FF]', sample))
                return True, url, len(feed.entries), has_arabic
    except Exception:
        pass
    return False, url, 0, False

def discover_rss_and_metadata(domain: str, default_name: str = None):
    for scheme in ['https', 'http']:
        base_url = f"{scheme}://{domain}"
        try:
            res = requests.get(base_url, headers=BROWSER_HEADERS, timeout=8, verify=False)
            if res.status_code == 200:
                html = res.text
                site_name = default_name
                if not site_name or len(site_name) > 35:
                    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        extracted = clean_arabic_title(title_match.group(1))
                        if re.search(r'[\u0600-\u06FF]', extracted):
                            site_name = extracted
                if not site_name:
                    site_name = domain

                # 1. Search <link> tags
                patterns = [
                    r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
                    r'<link[^>]+href=["\']([^"\']+)["\'][^>]*type=["\']application/(?:rss|atom)\+xml["\']'
                ]
                for pat in patterns:
                    for m in re.findall(pat, html, re.IGNORECASE):
                        candidate = urljoin(base_url, m)
                        valid, feed_url, count, is_news = test_feed(candidate)
                        if valid and is_news:
                            return feed_url, base_url, site_name, count

                # 2. Probe common paths
                for path in COMMON_FEED_PATHS:
                    candidate = urljoin(base_url, path)
                    valid, feed_url, count, is_news = test_feed(candidate)
                    if valid and is_news:
                        return feed_url, base_url, site_name, count
        except Exception:
            continue
    return None, None, None, 0

def resolve_msader_iframe(item):
    dfs_id, info = item
    try:
        r = requests.get(info['muta_url'], headers=BROWSER_HEADERS, timeout=8, verify=False)
        iframe = re.search(r'<iframe[^>]+src=[\"\'](https?://[^\"\']+)[\"\']', r.text, re.I)
        if iframe:
            domain = urlparse(iframe.group(1)).netloc.lower().replace('www.', '')
            if domain and domain not in IGNORE_DOMAINS:
                return domain, info['name']
    except Exception:
        pass
    return None, None

def probe_candidate(item):
    domain, name, origin = item
    if not check_dns(domain):
        return None
    feed_url, website, site_name, count = discover_rss_and_metadata(domain, name)
    if feed_url:
        return {
            'name': site_name,
            'domain': domain,
            'website': website,
            'feed_url': feed_url,
            'entries': count,
            'origin': origin,
        }
    return None


class Command(BaseCommand):
    help = 'Harvest, deduplicate, discover RSS, and auto-approve news sources from Sahaafa and Msader-ye'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Persist discovered sources as approved to DB')

    def handle(self, *args, **options):
        apply_mode = options['apply']
        self.stdout.write("=======================================================")
        self.stdout.write("  YEMEN PORTAL: EXTERNAL SOURCE HARVESTER & VERIFIER   ")
        self.stdout.write("=======================================================\n")

        # 1. Existing domains & names in Yemen Portal
        existing_domains = set()
        for link, site in Source.objects.values_list('link', 'website'):
            for u in (link, site):
                if u:
                    host = urlparse(u).netloc.lower().replace('www.', '')
                    if host:
                        existing_domains.add(host)

        existing_names = {s.strip() for s in Source.objects.values_list('name', flat=True) if s}
        candidates = {}  # domain -> (name, origin)

        # 2. Harvest Sahaafa.net (Directory + Categories)
        self.stdout.write("1. Harvesting all sources from sahaafa.net...")
        sahaafa_urls = [
            'https://sahaafa.net/sources.php',
            'https://sahaafa.net/index.php',
            'https://sahaafa.net/topic.php',
            'https://sahaafa.net/most_read.php',
        ] + [f'https://sahaafa.net/topic{i}.html' for i in range(1, 10)]

        for s_url in sahaafa_urls:
            try:
                res = requests.get(s_url, headers=BROWSER_HEADERS, timeout=10, verify=False)
                for dom, inner in re.findall(r'<a\s+[^>]*href=[\"\']/source/([^\"\'/]+)[\"\'][^>]*>(.*?)</a>', res.text, re.DOTALL | re.I):
                    dom = dom.strip().lower().replace('www.', '')
                    name = clean_arabic_title(inner)
                    if dom and dom not in existing_domains and dom not in IGNORE_DOMAINS:
                        if dom not in candidates:
                            candidates[dom] = (name, 'صحافة نت')
            except Exception:
                pass
        self.stdout.write(f"   Candidates after Sahaafa: {len(candidates)}")

        # 3. Harvest Msader-ye.net (All Categories + Pagination)
        self.stdout.write("2. Harvesting outlets from msader-ye.net across categories & pages...")
        categories = [63, 66, 55, 54, 22, 102, 104, 105]
        msader_outlets = {}  # dfs_id -> {'name': str, 'muta_url': str}

        target_pages = ['https://msader-ye.net/', 'https://msader-ye.net/?ac=mo']
        for cat in categories:
            target_pages.append(f'https://msader-ye.net/?d_f={cat}')
            target_pages.append(f'https://msader-ye.net/?d_f={cat}&pageNum_comment=1')
            target_pages.append(f'https://msader-ye.net/?d_f={cat}&min=30')

        for page_url in target_pages:
            try:
                r = requests.get(page_url, headers=BROWSER_HEADERS, timeout=10, verify=False)
                links = re.findall(r'<a\s+[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', r.text, re.DOTALL | re.I)
                last_muta = None
                for href, text in links:
                    muta_m = re.search(r'muta\.php\?no=(\d+)', href)
                    if muta_m:
                        last_muta = f"https://msader-ye.net/muta.php?no={muta_m.group(1)}"
                        continue
                    dfs_m = re.search(r'[?&]d_fs=(\d+)', href)
                    if dfs_m and last_muta:
                        dfs_id = dfs_m.group(1)
                        clean_name = clean_arabic_title(text)
                        if dfs_id not in msader_outlets and clean_name and len(clean_name) < 35:
                            msader_outlets[dfs_id] = {'name': clean_name, 'muta_url': last_muta}
                        last_muta = None
            except Exception:
                pass

        self.stdout.write(f"   Found {len(msader_outlets)} unique outlets on msader-ye. Resolving iframe domains (10 threads)...")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(resolve_msader_iframe, item) for item in msader_outlets.items()]
            for future in as_completed(futures):
                dom, name = future.result()
                if dom and dom not in existing_domains and dom not in IGNORE_DOMAINS:
                    if dom not in candidates:
                        candidates[dom] = (name, 'مصادر نت')

        # Filter against existing source names
        final_candidates = [
            (dom, name, origin) for dom, (name, origin) in candidates.items()
            if not name or name not in existing_names
        ]

        self.stdout.write(f"   Total Unique Candidates from both portals: {len(final_candidates)}")
        self.stdout.write(f"\n3. Probing candidates for active RSS feeds (10 threads)...")

        valid_sources = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(probe_candidate, c) for c in final_candidates]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    valid_sources.append(res)
                    self.stdout.write(self.style.SUCCESS(f"   [FOUND] {res['name']} ({res['domain']}) [{res['origin']}] -> {res['entries']} items"))

        self.stdout.write("\n================ IMPORT SUMMARY ================")
        self.stdout.write(f" Total Unique Candidates Probed: {len(final_candidates)}")
        self.stdout.write(f" Verified Active RSS Feeds     : {len(valid_sources)}")
        self.stdout.write(f" Apply Mode                    : {apply_mode}")
        self.stdout.write("================================================\n")

        if apply_mode and valid_sources:
            added = 0
            for item in valid_sources:
                if Source.objects.filter(link=item['feed_url']).exists():
                    continue
                Source.objects.create(
                    name=item['name'],
                    link=item['feed_url'],
                    website=item['website'],
                    source_type='أخبار عامة',
                    state=Source.State.VALID,
                    approve_state=Source.ApproveState.APPROVED,
                    brief_info=f"تم الاستيراد والتحقق تلقائياً من دليل {item['origin']}.",
                )
                added += 1
            self.stdout.write(self.style.SUCCESS(f"Successfully added and approved {added} new news sources!"))
        elif not apply_mode and valid_sources:
            self.stdout.write("Run with --apply to commit these verified sources to the database.")
