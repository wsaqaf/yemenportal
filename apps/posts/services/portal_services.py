import re
import logging
from decimal import Decimal
from datetime import timedelta
import requests
from django.core.cache import cache
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.posts.models import Post, Category, CurrencyRate
from apps.sources.models import Source

logger = logging.getLogger(__name__)

YEMEN_CITIES = [
    {"name": "صنعاء", "slug": "sanaa", "lat": 15.3694, "lon": 44.1910, "default_temp": 24, "icon": "☀️", "desc": "مشمس غالباً"},
    {"name": "عدن", "slug": "aden", "lat": 12.7855, "lon": 45.0187, "default_temp": 31, "icon": "🌤️", "desc": "غائم جزئياً"},
    {"name": "تعز", "slug": "taiz", "lat": 13.5795, "lon": 44.0209, "default_temp": 26, "icon": "⛅", "desc": "معتدل"},
    {"name": "المكلا", "slug": "mukalla", "lat": 14.5425, "lon": 49.1242, "default_temp": 30, "icon": "☀️", "desc": "صحو"},
    {"name": "مأرب", "slug": "marib", "lat": 15.4625, "lon": 45.3258, "default_temp": 29, "icon": "☀️", "desc": "صحو"},
    {"name": "الحديدة", "slug": "hodeidah", "lat": 14.7979, "lon": 42.9540, "default_temp": 32, "icon": "🌤️", "desc": "دافئ ورطب"},
]

DEFAULT_EXCHANGE_RATES = [
    {"region": "aden", "currency_code": "USD", "buy_price": Decimal("2055.00"), "sell_price": Decimal("2068.00")},
    {"region": "aden", "currency_code": "SAR", "buy_price": Decimal("538.00"), "sell_price": Decimal("541.00")},
    {"region": "sanaa", "currency_code": "USD", "buy_price": Decimal("535.00"), "sell_price": Decimal("538.00")},
    {"region": "sanaa", "currency_code": "SAR", "buy_price": Decimal("140.00"), "sell_price": Decimal("140.50")},
]


def _wmo_to_arabic(code: int) -> tuple[str, str]:
    if code == 0:
        return "☀️", "صحو ومشمس"
    if code in (1, 2, 3):
        return "⛅", "غائم جزئياً"
    if code in (45, 48):
        return "🌫️", "ضبابي"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "🌧️", "أمطار متفرقة"
    if code in (95, 96, 99):
        return "⛈️", "عواصف رعدية"
    return "🌤️", "معتدل"


def ensure_exchange_rates_seeded() -> None:
    """Seeds default Sana'a and Aden exchange rates if the table is empty."""
    if CurrencyRate.objects.count() == 0:
        for item in DEFAULT_EXCHANGE_RATES:
            CurrencyRate.objects.update_or_create(
                region=item["region"],
                currency_code=item["currency_code"],
                defaults={
                    "buy_price": item["buy_price"],
                    "sell_price": item["sell_price"],
                },
            )


def update_exchange_rates_from_recent_posts() -> int:
    """
    Scans recent approved economic posts for exchange rate numbers in Sana'a & Aden
    and updates CurrencyRate records when valid ranges are found.
    """
    ensure_exchange_rates_seeded()
    recent_posts = Post.objects.filter(
        state=Post.State.APPROVED,
        title__icontains="صرف",
    ).order_by("-published_at")[:15]

    updated_count = 0
    for post in recent_posts:
        text = f"{post.title} {post.description or ''}"
        # Look for Aden USD (1500 - 3000 range)
        aden_usd = re.search(r"عدن.*?الدولار.*?(\d{4})\s*(?:ريال|[-/]|بيع|شراء)?\s*(\d{4})?", text, re.DOTALL)
        if aden_usd:
            buy = Decimal(aden_usd.group(1))
            sell = Decimal(aden_usd.group(2)) if aden_usd.group(2) else buy + Decimal("12")
            if 1400 <= buy <= 3500 and 1400 <= sell <= 3500:
                CurrencyRate.objects.update_or_create(
                    region="aden",
                    currency_code="USD",
                    defaults={"buy_price": min(buy, sell), "sell_price": max(buy, sell)},
                )
                updated_count += 1
                break

    cache.delete("portal_exchange_rates")
    return updated_count


def get_exchange_rates() -> dict:
    """Returns cached Sana'a and Aden currency exchange rates."""
    cached = cache.get("portal_exchange_rates")
    if cached:
        return cached

    ensure_exchange_rates_seeded()
    rates = list(CurrencyRate.objects.all())
    sanaa_rates = [r for r in rates if r.region == "sanaa"]
    aden_rates = [r for r in rates if r.region == "aden"]
    latest_update = max((r.updated_at for r in rates), default=timezone.now())

    data = {
        "sanaa": sanaa_rates,
        "aden": aden_rates,
        "updated_at": latest_update,
    }
    cache.set("portal_exchange_rates", data, timeout=900)
    return data


def refresh_yemen_weather() -> list[dict]:
    """Fetches live weather for major Yemeni cities from Open-Meteo and caches in Redis."""
    results = []
    try:
        lats = ",".join(str(c["lat"]) for c in YEMEN_CITIES)
        lons = ",".join(str(c["lon"]) for c in YEMEN_CITIES)
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lats}&longitude={lons}"
            f"&current_weather=true&timezone=Asia%2FBMuscat"
        )
        resp = requests.get(url, timeout=3.5)
        if resp.status_code == 200:
            payload = resp.json()
            items = payload if isinstance(payload, list) else [payload]
            for idx, city in enumerate(YEMEN_CITIES):
                cw = items[idx].get("current_weather", {}) if idx < len(items) else {}
                temp = round(cw.get("temperature", city["default_temp"]))
                code = int(cw.get("weathercode", 0))
                icon, desc = _wmo_to_arabic(code)
                results.append({
                    "name": city["name"],
                    "slug": city["slug"],
                    "temp": temp,
                    "icon": icon,
                    "desc": desc,
                })
    except Exception as exc:
        logger.warning("Weather fetch fallback used: %s", exc)

    if not results:
        results = [
            {
                "name": c["name"],
                "slug": c["slug"],
                "temp": c["default_temp"],
                "icon": c["icon"],
                "desc": c["desc"],
            }
            for c in YEMEN_CITIES
        ]

    cache.set("portal_yemen_weather", results, timeout=3600)
    return results


def get_yemen_weather() -> list[dict]:
    """Returns cached weather for Yemen governorates without blocking requests."""
    cached = cache.get("portal_yemen_weather")
    if cached:
        return cached
    return [
        {
            "name": c["name"],
            "slug": c["slug"],
            "temp": c["default_temp"],
            "icon": c["icon"],
            "desc": c["desc"],
        }
        for c in YEMEN_CITIES
    ]


def get_homepage_portal_widgets() -> dict:
    """
    Returns Sahaafa-style portal blocks cached in Redis:
    - hero_post: Top breaking / featured post
    - readers_picks: Top 3 most read/voted stories
    - opinion_posts: Latest 6 opinion / columnist articles
    - top_sources: Top 12 active sources ranked by total reads
    """
    cached = cache.get("portal_homepage_widgets_v1")
    if cached:
        return cached

    now = timezone.now()
    base_qs = (
        Post.objects.filter(state=Post.State.APPROVED)
        .select_related("source", "topic")
        .prefetch_related("categories")
    )

    # 1. Hero Post: Prefer recent post with image and high activity or breaking category
    hero_post = (
        base_qs.filter(published_at__gte=now - timedelta(hours=24))
        .exclude(image_url__isnull=True)
        .exclude(image_url="")
        .order_by("-voting_result", "-post_views_count", "-published_at")
        .first()
    )
    if not hero_post:
        hero_post = (
            base_qs.exclude(image_url__isnull=True)
            .exclude(image_url="")
            .order_by("-published_at")
            .first()
        ) or base_qs.order_by("-published_at").first()

    exclude_ids = [hero_post.id] if hero_post else []

    # 2. Readers' Picks (اختيارات القراء - 3 cards)
    picks_qs = (
        base_qs.filter(published_at__gte=now - timedelta(hours=24))
        .exclude(id__in=exclude_ids)
        .order_by("-post_views_count", "-voting_result", "-published_at")[:3]
    )
    readers_picks = list(picks_qs)
    if len(readers_picks) < 3:
        extra_ids = exclude_ids + [p.id for p in readers_picks]
        fallback_picks = list(
            base_qs.exclude(id__in=extra_ids)
            .order_by("-post_views_count", "-voting_result", "-published_at")[: 3 - len(readers_picks)]
        )
        readers_picks.extend(fallback_picks)

    # 3. Opinion & Columnists (مقالات وآراء) - bounded to recent 30 days for index speed
    opinion_cat_ids = list(
        Category.objects.filter(
            name__in=["آراء", "كتاب من اليمن", "مقالات", "تقارير", "بانوراما"]
        ).values_list("id", flat=True)
    )
    opinion_posts = list(
        base_qs.filter(
            published_at__gte=now - timedelta(days=30),
            categories__id__in=opinion_cat_ids,
        )
        .order_by("-published_at")[:6]
    )
    # Deduplicate in Python to avoid expensive SQL DISTINCT on M2M
    seen_op_ids = set()
    unique_opinion_posts = []
    for p in opinion_posts:
        if p.id not in seen_op_ids:
            seen_op_ids.add(p.id)
            unique_opinion_posts.append(p)
    opinion_posts = unique_opinion_posts

    if len(opinion_posts) < 4:
        existing_op_ids = [p.id for p in opinion_posts] + exclude_ids
        opinion_posts.extend(
            list(
                base_qs.filter(published_at__gte=now - timedelta(days=7))
                .exclude(id__in=existing_op_ids)
                .order_by("-published_at")[: 6 - len(opinion_posts)]
            )
        )

    # 4. Top Sources Directory (دليل المواقع / المصادر النشطة) - cached 1h & bounded to 14 days
    top_sources = cache.get("portal_top_sources_v1")
    if not top_sources:
        recent_cutoff = now - timedelta(days=14)
        top_sources = list(
            Source.objects.filter(
                approve_state=Source.ApproveState.APPROVED,
                state=Source.State.VALID,
                posts__published_at__gte=recent_cutoff,
                posts__state=Post.State.APPROVED,
            )
            .annotate(
                total_reads=Sum("posts__post_views_count"),
                posts_total=Count("posts"),
            )
            .order_by("-total_reads", "-posts_total")[:12]
        )
        cache.set("portal_top_sources_v1", top_sources, timeout=3600)

    data = {
        "hero_post": hero_post,
        "readers_picks": readers_picks,
        "opinion_posts": opinion_posts,
        "top_sources": top_sources,
    }
    cache.set("portal_homepage_widgets_v1", data, timeout=600)
    return data


def get_economic_posts(limit: int = 15) -> list[Post]:
    """
    Fast, Redis-cached query for recent economic and exchange-rate news.
    Avoids full-table M2M joins and COUNT(*) queries.
    """
    cache_key = f"portal_economic_posts_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now = timezone.now()
    recent_qs = (
        Post.objects.filter(
            state=Post.State.APPROVED,
            published_at__gte=now - timedelta(days=30),
        )
        .filter(
            Q(title__icontains="صرف")
            | Q(title__icontains="الريال")
            | Q(title__icontains="الدولار")
            | Q(title__icontains="البنك")
            | Q(title__icontains="اقتصاد")
            | Q(title__icontains="العملات")
            | Q(title__icontains="الذهب")
        )
        .select_related("source", "topic")
        .prefetch_related("categories")
        .order_by("-published_at")[:limit]
    )
    posts = list(recent_qs)
    if not posts:
        posts = list(
            Post.objects.filter(state=Post.State.APPROVED)
            .select_related("source", "topic")
            .prefetch_related("categories")
            .order_by("-published_at")[:limit]
        )
    cache.set(cache_key, posts, timeout=600)
    return posts

