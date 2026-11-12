import re
import time
import logging
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)

# List of aggressive AI scrapers, SEO bots, and commercial crawlers
# that aggressively scrape without editorial or search traffic value to YemenPortal.
BLOCKED_BOT_REGEX = re.compile(
    r'(Baiduspider|DotBot|Amazonbot|ClaudeBot|SemrushBot|SERankingBacklinksBot|'
    r'Bytespider|KeenableBot|Reflectionbot|PetalBot|MJ12bot|AhrefsBot|'
    r'DataForSeoBot|BLEXBot|Seekport|ZoominfoBot|CensysInspect|Barkrowler)',
    re.IGNORECASE
)

# General crawler signature for impression fraud prevention
ANY_BOT_REGEX = re.compile(r'(bot|spider|crawl|scraper|headless|archiver|phantom)', re.IGNORECASE)


class BotThrottlingMiddleware:
    """
    1. Blocks aggressive scrapers before database/template execution.
    2. Drops fake impression recording from headless crawlers.
    3. Rate limits high-frequency IP flooding via Redis.
    """
    # Rate limit: Max 180 requests per 60-second window per IP
    RATE_LIMIT_MAX_REQUESTS = 180
    RATE_LIMIT_WINDOW_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Exempt static assets, health checks, and service worker files
        if path.startswith(('/static/', '/media/', '/favicon.ico', '/manifest', '/sw.js')):
            return self.get_response(request)

        # 1. Block aggressive non-search scrapers
        if user_agent and BLOCKED_BOT_REGEX.search(user_agent):
            return HttpResponseForbidden("Access restricted for automated scrapers.")

        # 2. Block fake impression recording from all bots & crawlers
        if path.startswith('/posts/record-impressions/') and ANY_BOT_REGEX.search(user_agent):
            return JsonResponse({'status': 'ignored', 'reason': 'bot'}, status=200)

        # 3. Rate limiting per IP (sliding window via Redis cache)
        client_ip = self._get_client_ip(request)
        if client_ip and client_ip not in ('127.0.0.1', '::1'):
            if self._is_rate_limited(client_ip):
                logger.warning(f"Rate limited client IP: {client_ip} on path {path}")
                return HttpResponse(
                    "Too Many Requests. Please slow down.",
                    status=429,
                    headers={'Retry-After': '30', 'Content-Type': 'text/plain; charset=utf-8'}
                )

        return self.get_response(request)

    def _get_client_ip(self, request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # First IP in X-Forwarded-For is the real client
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')

    def _is_rate_limited(self, ip: str) -> bool:
        current_minute = int(time.time() // self.RATE_LIMIT_WINDOW_SECONDS)
        cache_key = f"ratelimit:{ip}:{current_minute}"

        try:
            # Atomic increment
            req_count = cache.incr(cache_key)
        except ValueError:
            # Key does not exist yet
            cache.set(cache_key, 1, timeout=self.RATE_LIMIT_WINDOW_SECONDS + 5)
            req_count = 1
        except Exception as e:
            # Redis failure should fail open to not block legitimate users
            return False

        return req_count > self.RATE_LIMIT_MAX_REQUESTS
