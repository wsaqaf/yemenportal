import re
import socket
import argparse
from urllib.parse import urlparse, urljoin
import requests
import feedparser

import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.sources.models import Source
from apps.posts.models import Post

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
}

COMMON_FEED_PATHS = [
    '/feed', '/feed/', '/rss', '/rss.xml', '/?feed=rss2', '/rss.php', '/feed/home.xml'
]

def check_dns(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except (socket.gaierror, socket.herror):
        return False

def clean_url(url: str) -> str:
    url = (url or '').strip()
    # Fix leading slashes like /http://...
    url = re.sub(r'^/+(https?://)', r'\1', url)
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url.lstrip('/')
    return url

def test_feed(url: str):
    """Tests if a URL returns a parseable RSS/Atom feed."""
    try:
        res = requests.get(url, headers=BROWSER_HEADERS, timeout=10, verify=False)
        if res.status_code == 200:
            feed = feedparser.parse(res.content)
            if len(feed.entries) > 0:
                # News validation: check if entries contain readable Arabic text
                sample = (feed.entries[0].get('title', '') + ' ' + feed.entries[0].get('summary', ''))
                has_arabic = bool(re.search(r'[\u0600-\u06FF]', sample))
                return True, url, len(feed.entries), has_arabic
    except Exception:
        pass
    return False, url, 0, False

def auto_discover_rss(base_url: str):
    """Attempts to discover active RSS feeds from domain homepage or common paths."""
    try:
        parsed = urlparse(base_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        
        # 1. Fetch homepage and check link tags
        res = requests.get(root, headers=BROWSER_HEADERS, timeout=8, verify=False)
        if res.status_code == 200:
            html = res.text
            patterns = [
                r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*href=["\']([^"\']+)["\']',
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]*type=["\']application/(?:rss|atom)\+xml["\']'
            ]
            for pat in patterns:
                matches = re.findall(pat, html, re.IGNORECASE)
                for m in matches:
                    candidate = urljoin(root, m)
                    valid, working_url, count, is_news = test_feed(candidate)
                    if valid:
                        return working_url, count, is_news

        # 2. Try common feed fallback paths
        for path in COMMON_FEED_PATHS:
            candidate = urljoin(root, path)
            valid, working_url, count, is_news = test_feed(candidate)
            if valid:
                return working_url, count, is_news
    except Exception:
        pass
    return None, 0, False

def audit_all_sources(apply_changes=False):
    sources = Source.objects.all().order_by('name')
    total = sources.count()

    results = {
        'working': [],
        'repaired': [],
        'archived': [],
        'purged': [],
        'blocked_403': []
    }

    print(f"\n=======================================================")
    print(f"  YEMEN PORTAL: AUDITING {total} SOURCES (Apply: {apply_changes})")
    print(f"=======================================================\n")

    for idx, src in enumerate(sources, 1):
        cleaned = clean_url(src.link)
        domain = urlparse(cleaned).netloc
        post_count = src.posts.count()

        # Step 1: DNS Check
        if not check_dns(domain):
            if post_count == 0:
                results['purged'].append((src, 'DNS Resolution Failure (NXDOMAIN)'))
                if apply_changes:
                    src.delete()
            else:
                results['archived'].append((src, f'DNS Dead, kept {post_count} posts'))
                if apply_changes:
                    src.state = Source.State.INVALID
                    src.approve_state = Source.ApproveState.REJECTED
                    src.save(update_fields=['state', 'approve_state'])
            continue

        # Step 2: Test Current URL
        is_valid, working_url, entries, is_news = test_feed(cleaned)

        if is_valid:
            if cleaned != src.link:
                results['repaired'].append((src, cleaned, entries))
                if apply_changes:
                    src.link = cleaned
                    src.state = Source.State.VALID
                    src.approve_state = Source.ApproveState.APPROVED
                    src.save(update_fields=['link', 'state', 'approve_state'])
            else:
                results['working'].append((src, entries))
                if apply_changes:
                    src.state = Source.State.VALID
                    src.approve_state = Source.ApproveState.APPROVED
                    src.save(update_fields=['state', 'approve_state'])
            continue

        # Step 3: Attempt Auto-Discovery
        discovered_url, d_entries, d_news = auto_discover_rss(cleaned)
        if discovered_url:
            results['repaired'].append((src, discovered_url, d_entries))
            if apply_changes:
                src.link = discovered_url
                src.state = Source.State.VALID
                src.approve_state = Source.ApproveState.APPROVED
                src.save(update_fields=['link', 'state', 'approve_state'])
            continue

        # Step 4: Check if Blocked (403 Forbidden) vs Truly Dead
        try:
            head = requests.head(cleaned, headers=BROWSER_HEADERS, timeout=6, verify=False)
            status = head.status_code
        except Exception:
            status = 0

        if status == 403:
            results['blocked_403'].append((src, post_count))
            if apply_changes:
                # Keep active for custom crawler headers
                src.state = Source.State.VALID
                src.save(update_fields=['state'])
        elif post_count == 0:
            results['purged'].append((src, f'HTTP {status} Dead & 0 posts'))
            if apply_changes:
                src.delete()
        else:
            results['archived'].append((src, f'HTTP {status} Dead, kept {post_count} posts'))
            if apply_changes:
                src.state = Source.State.INVALID
                src.approve_state = Source.ApproveState.REJECTED
                src.save(update_fields=['state', 'approve_state'])

    print("\n================ AUDIT SUMMARY ================")
    print(f" Active & Valid Feeds      : {len(results['working'])}")
    print(f" Repaired Feeds            : {len(results['repaired'])}")
    print(f" Cloudflare/403 Preserved  : {len(results['blocked_403'])}")
    print(f" Archived Dead (Saved Posts): {len(results['archived'])}")
    print(f" Purged Dead (0 Posts)     : {len(results['purged'])}")
    print("===============================================\n")

    if results['repaired']:
        print("--- TOP REPAIRED FEEDS SAMPLE ---")
        for s, new_link, entries in results['repaired'][:10]:
            print(f"  [FIXED] {s.name} -> {new_link} ({entries} entries)")

    if results['purged']:
        print("\n--- SAMPLE PURGED DEFUNT SOURCES (0 Posts) ---")
        for s, reason in results['purged'][:10]:
            print(f"  [DELETED] {s.name} ({reason})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Apply changes to database')
    args = parser.parse_args()
    audit_all_sources(apply_changes=args.apply)
