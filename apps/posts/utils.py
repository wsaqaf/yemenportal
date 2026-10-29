import ssl, urllib.parse, urllib.request
from django.core.cache import cache

BOT_CHALLENGE_KEYWORDS = [
    'cf-browser-verification', 'challenge-platform', 'cf_chl_prog',
    'just a moment...', 'ddos-guard', 'incapsula', 'checking your browser',
    'cloudflare-static', 'bot verification'
]

def is_iframe_allowed(url, source=None):
    """
    Checks if a URL allows iframe embedding and doesn't enforce bot challenges.
    Caches the verdict for 7 days.
    """
    if source and not source.iframe_flag:
        return False
    if not url:
        return True

    domain = urllib.parse.urlparse(url).netloc.lower()
    if not domain:
        return True

    cache_key = f'iframe_ok_{domain}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    allows = True
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=3.0, context=ctx) as r:
            headers = {k.lower(): v for k, v in r.headers.items()}
            xf = headers.get('x-frame-options', '').upper()
            csp = headers.get('content-security-policy', '').lower()
            server = headers.get('server', '').lower()
            cf_mitigated = headers.get('cf-mitigated', '').lower()

            # 1. فحص ترويسات منع الإطارات
            if 'DENY' in xf or 'SAMEORIGIN' in xf or "'self'" in csp or "'none'" in csp:
                allows = False
            # 2. فحص أنظمة الحماية من البوتات
            elif cf_mitigated == 'challenge' or r.status in [403, 503]:
                allows = False
            else:
                # قراءة بداية الصفحة لكشف أكواد Cloudflare Challenge
                sample = r.read(4000).decode('utf-8', errors='ignore').lower()
                if any(w in sample for w in BOT_CHALLENGE_KEYWORDS):
                    allows = False

    except urllib.error.HTTPError as e:
        # إذا رد السيرفر بـ 403/503 فهو خلف جدار حماية
        if e.code in [403, 503]:
            allows = False
    except Exception:
        allows = source.iframe_flag if source else True

    cache.set(cache_key, allows, timeout=60 * 60 * 24 * 7)

    if not allows and source and source.iframe_flag:
        source.iframe_flag = False
        source.save(update_fields=['iframe_flag'])

    return allows
