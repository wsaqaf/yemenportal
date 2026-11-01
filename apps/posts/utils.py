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
    Caches the verdict for 30 days. Automatically marks source.iframe_flag = False if blocked.
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
        with urllib.request.urlopen(req, timeout=3.5, context=ctx) as r:
            if r.status != 200:
                allows = False
            else:
                # 1. فحص جميع ترويسات X-Frame-Options (سواء فردية أو مكررة)
                for xf in r.headers.get_all('x-frame-options', []):
                    xf_u = xf.upper()
                    if 'DENY' in xf_u or 'SAMEORIGIN' in xf_u:
                        allows = False
                        break

                # 2. فحص جميع ترويسات Content-Security-Policy (سواء فردية أو مكررة)
                if allows:
                    for csp in r.headers.get_all('content-security-policy', []):
                        csp_l = csp.lower()
                        # فحص تعليمة frame-ancestors الصريحة
                        if 'frame-ancestors' in csp_l:
                            if 'yemenportal.net' not in csp_l and 'frame-ancestors *' not in csp_l:
                                allows = False
                                break
                        elif "'self'" in csp_l or "'none'" in csp_l:
                            if 'frame-ancestors' in csp_l or 'default-src' in csp_l:
                                allows = False
                                break

                # 3. فحص أنظمة الحماية من البوتات والجدران النارية
                if allows:
                    cf_mitigated = (r.headers.get('cf-mitigated') or '').lower()
                    if cf_mitigated == 'challenge':
                        allows = False
                    else:
                        sample = r.read(4000).decode('utf-8', errors='ignore').lower()
                        if any(w in sample for w in BOT_CHALLENGE_KEYWORDS):
                            allows = False

    except urllib.error.HTTPError:
        # إذا رد السيرفر بأي خطأ فهو خلف حماية أو يمنع التضمين
        allows = False
    except Exception:
        # إذا فشل الاتصال أو حدث timeout/SSL error، فلا نفترض السماح لأن المتصفح سيفشل أيضاً
        allows = False

    cache.set(cache_key, allows, timeout=60 * 60 * 24 * 30)

    if not allows and source and source.iframe_flag:
        source.iframe_flag = False
        source.save(update_fields=['iframe_flag'])

    return allows
