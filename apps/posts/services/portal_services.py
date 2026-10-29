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

YEMEN_CORE_KEYWORDS = [
    "اليمن", "يمني", "اليمنية", "اليمنيين", "صنعاء", "عدن", "تعز", "مأرب", "مارب",
    "حضرموت", "الحديدة", "شبوة", "صعدة", "المكلا", "الضالع", "لحج", "أبين", "ابين",
    "المهرة", "سقطرى", "البيضاء", "الجوف", "ذمار", "عمران", "حجة", "المحويت", "ريمة",
    "الحوثي", "الحوثيين", "الحوثية", "الانتقالي", "الشرعية", "مجلس القيادة", "العليمي",
    "الحكومة اليمنية", "القوات المسلحة", "مطار عدن", "باب المندب", "البحر الأحمر",
    "الريال اليمني", "البنك المركزي", "سبأ", "تهامة", "يافع", "رداع", "بيحان", "المخا",
]

BREAKING_KEYWORDS = [
    "عاجل", "انفجار", "استهداف", "قصف", "مطار عدن", "معارك", "القوات المسلحة",
    "تحرير", "هجوم", "غارات", "مجلس الأمن", "قرار جمهوري", "البنك المركزي",
    "انهيار", "قتيل", "ضحايا", "تحذير", "حصار", "انتصارات", "طيران", "صاروخ",
]

OFF_TOPIC_KEYWORDS = [
    "التوقيت الشتوي في مصر", "دار الإفتاء المصرية", "سفينة نوح", "البرلمان الألباني",
    "كأس الرابطة الإنجليزية", "ليفربول", "مانشستر", "برشلونة", "ريال مدريد",
    "الارتقاء بإفريقيا", "أكرا", "الدوري الإنجليزي", "أصل مياه الأرض",
]

NON_YEMEN_GENERAL_SOURCES = [
    "البوابة نيوز", "روسيا اليوم", "سبوتنيك", "اليوم السابع", "المصري اليوم",
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


def get_source_activity_weights() -> dict[int, dict]:
    """
    Computes on-the-fly dynamic weights per source and section over the latest 1,500 posts:
    - yemen_ratio (0.0 .. 1.0): fraction of the source's recent posts that are about Yemen
    - activity_score (0.0 .. 25.0): publishing frequency + reader engagement
    - section_bonus (-20.0 .. +20.0): based on whether the feed/source name is a local news section vs sports/variety
    - total_weight: composite weight applied on the fly when ranking stories
    """
    cached = cache.get("portal_dynamic_source_weights_v2")
    if cached is not None:
        return cached

    from collections import defaultdict

    recent_posts = list(
        Post.objects.filter(state=Post.State.APPROVED)
        .select_related("source")
        .only("id", "title", "description", "source_id", "post_views_count", "source__name", "source__website")
        .order_by("-published_at")[:1500]
    )

    totals = defaultdict(int)
    yemen_hits = defaultdict(int)
    views_sum = defaultdict(int)
    source_meta = {}

    for p in recent_posts:
        sid = p.source_id
        if not sid:
            continue
        totals[sid] += 1
        views_sum[sid] += (p.post_views_count or 0)
        if sid not in source_meta and p.source:
            source_meta[sid] = (p.source.name or "", p.source.website or "")
        text = f"{p.title or ''} {p.description or ''}"
        if any(kw in text for kw in YEMEN_CORE_KEYWORDS):
            yemen_hits[sid] += 1

    weights: dict[int, dict] = {}
    for sid, total_cnt in totals.items():
        yh = yemen_hits[sid]
        raw_ratio = yh / total_cnt if total_cnt > 0 else 0.0
        src_name, src_web = source_meta.get(sid, ("", ""))

        # Structural domain/name indicator for Yemeni outlets
        yemen_markers = ["يمن", "عدن", "تعز", "سبأ", "صحوة", "مأرب", "حضرموت", "المصدر", "كريتر", "المهرية", "بلقيس", "حشد", "المنتصف", "الأمناء", "يافع", "تهامة", "شمسان"]
        has_yemen_brand = any(m in src_name for m in yemen_markers) or ".ye" in src_web or "yemen" in src_web.lower()

        # Bayesian smoothing for sources with very few posts in sample
        prior = 0.75 if has_yemen_brand else 0.15
        yemen_ratio = ((yh + (3 * prior)) / (total_cnt + 3))

        # Section / Sub-feed modifier from source name (e.g. "- أخبار وتقارير" vs "- ثقافة وفن" / "- رياضة")
        section_bonus = 0.0
        if any(sec in src_name for sec in ["أخبار", "محلي", "تقارير", "اليمن"]):
            section_bonus += 12.0
        if any(sec in src_name for sec in ["رياضة", "ثقافة", "فن", "منوعات", "تكنولوجيا", "مرأة"]):
            section_bonus -= 18.0

        # Activity & readership score (0..25)
        activity_score = min(12.0, total_cnt * 0.25) + min(13.0, views_sum[sid] * 0.08)

        # Composite weight: heavily reward high Yemen focus ratio, penalize < 25% Yemen focus
        focus_points = yemen_ratio * 55.0
        penalty = -45.0 if yemen_ratio < 0.25 else 0.0
        total_weight = round(focus_points + activity_score + section_bonus + penalty, 2)

        weights[sid] = {
            "yemen_ratio": round(yemen_ratio, 3),
            "activity_score": round(activity_score, 2),
            "section_bonus": section_bonus,
            "total_weight": total_weight,
        }

    cache.set("portal_dynamic_source_weights_v2", weights, timeout=900)
    return weights


def get_category_section_weight(post: Post) -> float:
    """Computes section/category weight on the fly from the post's assigned categories."""
    high_yemen_cats = {"عاجل": 25.0, "محلي": 20.0, "أخبار": 12.0, "تقارير": 12.0, "اقتصاد": 10.0}
    low_priority_cats = {"رياضة": -20.0, "ثقافة وفن": -15.0, "تكنولوجيا": -15.0, "منوعات": -15.0, "عربي": -10.0, "دولي": -10.0}

    bonus = 0.0
    for cat in post.categories.all():
        if cat.name in high_yemen_cats:
            bonus += high_yemen_cats[cat.name]
        elif cat.name in low_priority_cats:
            bonus += low_priority_cats[cat.name]
    return max(-25.0, min(30.0, bonus))


def is_yemen_relevant(post: Post) -> bool:
    """Returns True if a post is genuinely about Yemen or major regional events affecting Yemen."""
    title = post.title or ""
    desc = post.description or ""
    combined = f"{title} {desc}"

    if any(bad in combined for bad in OFF_TOPIC_KEYWORDS):
        return False

    has_yemen_kw = any(kw in combined for kw in YEMEN_CORE_KEYWORDS)
    if has_yemen_kw:
        return True

    source_name = post.source.name if post.source else ""
    if any(src in source_name for src in NON_YEMEN_GENERAL_SOURCES):
        return False

    yemen_source_markers = [
        "يمن", "عدن", "تعز", "سبأ", "صحوة", "مأرب", "حضرموت", "المصدر",
        "كريتر", "المهرية", "بلقيس", "الحدث", "حشد", "المنتصف", "الأمناء", "يافع",
    ]
    if any(m in source_name for m in yemen_source_markers):
        return True

    return False


def score_yemen_post(post: Post, source_weights: dict[int, dict], now=None) -> float:
    """
    Scores a post prioritizing:
    1. Explicit Yemen relevance (title/description keywords)
    2. Cluster size (topic_size - number of independent sources covering the story)
    3. Dynamic Source Yemen-Focus Ratio, Activity & Section Weight (computed on the fly)
    4. Category / Section Weight (عاجل, محلي, تقارير vs رياضة, منوعات)
    5. Breaking / Urgent political, military, economic, or humanitarian keywords
    6. Reader engagement (views & votes) + valid image presence + recency
    """
    if now is None:
        now = timezone.now()

    title = post.title or ""
    desc = post.description or ""

    score = 0.0

    # 1. Explicit Yemen keyword in title (+65) or description (+30)
    if any(kw in title for kw in YEMEN_CORE_KEYWORDS):
        score += 65.0
    elif any(kw in desc for kw in YEMEN_CORE_KEYWORDS):
        score += 30.0

    # 2. Cluster size (multi-source coverage is a primary signal of national importance)
    topic_size = post.topic.topic_size if post.topic_id and post.topic else 1
    if topic_size and topic_size > 1:
        if "أسعار صرف العملات" in title:
            score += min(topic_size, 4) * 8.0
        else:
            score += min(topic_size, 15) * 18.0

    # 3. Dynamic Source Yemen-Focus Ratio + Activity + Section Weight
    src_info = source_weights.get(post.source_id, {})
    if isinstance(src_info, dict):
        score += src_info.get("total_weight", 0.0)
    else:
        score += float(src_info or 0.0)

    # 4. Category / Section weight on the fly
    score += get_category_section_weight(post)

    # 5. Breaking / Major event keywords in title (+35)
    if any(bkw in title for bkw in BREAKING_KEYWORDS):
        score += 35.0

    # 6. Reader engagement (views + votes)
    views = post.post_views_count or 0
    votes = post.voting_result or 0
    score += (min(views, 500) * 6.0) + (votes * 20.0)

    # 7. Visual completeness bonus (+10 if post has an image)
    if post.image_url and post.image_url.startswith("http"):
        score += 10.0

    # 8. Recency bonus (up to +24 points for stories in the last 8 hours)
    age_hours = max(0.0, (now - post.published_at).total_seconds() / 3600.0)
    score += max(0.0, 24.0 - (age_hours * 2.5))

    return score


def get_ranked_yemen_posts(hours: int = 24, limit: int = 30) -> list[Post]:
    """
    Returns top Yemen-focused & breaking news stories ordered by composite importance score
    (Yemen relevance + Cluster size + Source activity + Breaking keywords + Views/Votes)
    and deduplicated by topic_id.
    """
    now = timezone.now()
    source_weights = get_source_activity_weights()
    base_qs = (
        Post.objects.filter(state=Post.State.APPROVED)
        .select_related("source", "topic")
        .prefetch_related("categories")
    )

    candidates = list(
        base_qs.filter(published_at__gte=now - timedelta(hours=hours))
        .order_by("-published_at")[:450]
    )
    if len(candidates) < 10:
        candidates = list(
            base_qs.filter(published_at__gte=now - timedelta(days=7))
            .order_by("-published_at")[:450]
        )

    yemen_candidates = [p for p in candidates if is_yemen_relevant(p)]
    if not yemen_candidates:
        yemen_candidates = candidates

    # Map topic_id -> fallback image_url from any sibling post in the same cluster
    topic_images: dict[int, str] = {}
    for p in yemen_candidates:
        if p.topic_id and p.image_url and p.image_url.startswith("http") and p.topic_id not in topic_images:
            topic_images[p.topic_id] = p.image_url

    scored = sorted(
        yemen_candidates,
        key=lambda p: (
            score_yemen_post(p, source_weights=source_weights, now=now),
            p.topic.topic_size if p.topic_id and p.topic else 0,
            p.post_views_count or 0,
            p.published_at,
        ),
        reverse=True,
    )

    # Deduplicate by topic_id and normalized title prefix so identical stories don't repeat
    seen_topics = set()
    seen_titles = set()
    unique_posts = []
    for post in scored:
        if post.topic_id and post.topic_id in seen_topics:
            continue
        title_key = (post.title or "").strip()[:45]
        if title_key in seen_titles:
            continue
        if post.topic_id:
            seen_topics.add(post.topic_id)
            if not post.image_url and post.topic_id in topic_images:
                post.image_url = topic_images[post.topic_id]
        seen_titles.add(title_key)
        unique_posts.append(post)
        if len(unique_posts) >= limit:
            break

    return unique_posts


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
    - hero_post: Top breaking / major Yemen story (with cluster size & source activity weighting)
    - readers_picks: Top 3 important/most-read Yemen stories
    - opinion_posts: Latest 6 opinion / columnist articles
    - top_sources: Top 12 active sources ranked by total reads
    """
    cached = cache.get("portal_homepage_widgets_v4")
    if cached:
        return cached

    now = timezone.now()
    base_qs = (
        Post.objects.filter(state=Post.State.APPROVED)
        .select_related("source", "topic")
        .prefetch_related("categories")
    )

    ranked_yemen = get_ranked_yemen_posts(hours=24, limit=15)

    # 1. Hero Post: Prefer the #1 ranked Yemen breaking cluster/story
    hero_post = ranked_yemen[0] if ranked_yemen else base_qs.order_by("-published_at").first()

    # 2. Readers' Picks (اختيارات القراء - next 3 top Yemen stories)
    readers_picks = ranked_yemen[1:4] if len(ranked_yemen) >= 4 else ranked_yemen[1:]

    # 3. Opinion & Columnists (مقالات وآراء) - bounded to recent 30 days for index speed
    opinion_cat_ids = list(
        Category.objects.filter(
            name__in=["آراء", "كتاب من اليمن", "مقالات", "تقارير", "بانوراما"]
        ).values_list("id", flat=True)
    )
    raw_opinions = list(
        base_qs.filter(
            published_at__gte=now - timedelta(days=30),
            categories__id__in=opinion_cat_ids,
        )
        .order_by("-published_at")[:18]
    )
    seen_op_ids = set()
    opinion_posts = []
    for p in raw_opinions:
        if p.id not in seen_op_ids and is_yemen_relevant(p):
            seen_op_ids.add(p.id)
            opinion_posts.append(p)
            if len(opinion_posts) >= 6:
                break

    if len(opinion_posts) < 4:
        for p in ranked_yemen[4:]:
            if p.id not in seen_op_ids:
                seen_op_ids.add(p.id)
                opinion_posts.append(p)
                if len(opinion_posts) >= 6:
                    break

    # 4. Top Sources Directory (دليل المواقع / المصادر النشطة) - weighted by on-the-fly Yemen Focus Ratio
    top_sources = cache.get("portal_top_sources_v3")
    if not top_sources:
        source_weights = get_source_activity_weights()
        recent_cutoff = now - timedelta(days=14)
        candidate_sources = list(
            Source.objects.filter(
                approve_state=Source.ApproveState.APPROVED,
                state=Source.State.VALID,
                posts__published_at__gte=recent_cutoff,
                posts__state=Post.State.APPROVED,
            )
            .exclude(name__in=NON_YEMEN_GENERAL_SOURCES)
            .annotate(
                total_reads=Sum("posts__post_views_count"),
                posts_total=Count("posts"),
            )
            .order_by("-total_reads", "-posts_total")[:30]
        )
        # Filter to sources with >= 35% Yemen focus ratio and sort by Yemen-weighted readership
        yemen_sources = [
            s for s in candidate_sources
            if source_weights.get(s.id, {}).get("yemen_ratio", 0.5) >= 0.35
        ]
        yemen_sources.sort(
            key=lambda s: (
                (s.total_reads or s.posts_total or 0) * source_weights.get(s.id, {}).get("yemen_ratio", 0.5),
                s.posts_total or 0,
            ),
            reverse=True,
        )
        top_sources = yemen_sources[:12]
        cache.set("portal_top_sources_v3", top_sources, timeout=3600)

    data = {
        "hero_post": hero_post,
        "readers_picks": readers_picks,
        "opinion_posts": opinion_posts,
        "top_sources": top_sources,
    }
    cache.set("portal_homepage_widgets_v4", data, timeout=600)
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
        )
        .select_related("source", "topic")
        .prefetch_related("categories")
        .order_by("-published_at")[: limit * 2]
    )
    posts = [p for p in recent_qs if is_yemen_relevant(p)][:limit]
    if not posts:
        posts = list(recent_qs[:limit])
    cache.set(cache_key, posts, timeout=600)
    return posts
