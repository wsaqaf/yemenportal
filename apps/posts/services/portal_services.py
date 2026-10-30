import re
import logging
from decimal import Decimal
from datetime import timedelta
import requests
from django.core.cache import cache
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.posts.models import Post, Category, CurrencyRate, Topic
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

    # Age of the post in hours & freshness decay factor (half-life of ~3 hours)
    age_hours = max(0.0, (now - post.published_at).total_seconds() / 3600.0)
    recency_decay = 1.0 / (1.0 + (age_hours / 3.0) ** 1.8)

    # 2. Cluster size (multi-source coverage weighted by freshness velocity)
    topic_size = post.topic.topic_size if post.topic_id and post.topic else 1
    if topic_size and topic_size > 1:
        if "أسعار صرف العملات" in title:
            score += min(topic_size, 4) * 8.0 * recency_decay
        else:
            score += min(topic_size, 12) * 16.0 * recency_decay

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

    # 8. Recency bonus (up to +35 points for fresh stories in the last 4 hours)
    score += max(0.0, 35.0 - (age_hours * 6.0))

    return score


def get_ranked_yemen_posts(hours: int = 4, limit: int = 30) -> list[Post]:
    """
    Returns top Yemen-focused & breaking news stories ordered by composite importance score
    (Yemen relevance + Cluster size + Source activity + Breaking keywords + Views/Votes)
    and deduplicated by topic_id, using the freshest headline per topic.
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
    if len(candidates) < 15:
        candidates = list(
            base_qs.filter(published_at__gte=now - timedelta(hours=8))
            .order_by("-published_at")[:450]
        )
    if len(candidates) < 10:
        candidates = list(
            base_qs.filter(published_at__gte=now - timedelta(days=2))
            .order_by("-published_at")[:450]
        )

    yemen_candidates = [p for p in candidates if is_yemen_relevant(p)]
    if not yemen_candidates:
        yemen_candidates = candidates

    # Map topic_id -> fallback image_url and latest post in cluster
    topic_images: dict[int, str] = {}
    topic_latest: dict[int, Post] = {}
    for p in yemen_candidates:
        if p.topic_id:
            if p.image_url and p.image_url.startswith("http") and p.topic_id not in topic_images:
                topic_images[p.topic_id] = p.image_url
            if p.topic_id not in topic_latest or p.published_at > topic_latest[p.topic_id].published_at:
                topic_latest[p.topic_id] = p

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
        rep_post = post
        if post.topic_id:
            if post.topic_id in seen_topics:
                continue
            seen_topics.add(post.topic_id)
            latest_p = topic_latest.get(post.topic_id)
            # If there is a newer update in this topic (> 15 mins later), use the newest post for headline & image
            if latest_p and (latest_p.published_at - post.published_at).total_seconds() > 900:
                rep_post = latest_p
            if not rep_post.image_url and post.topic_id in topic_images:
                rep_post.image_url = topic_images[post.topic_id]

        title_key = (rep_post.title or "").strip()[:45]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        unique_posts.append(rep_post)
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


THEMATIC_SECTIONS_SPEC = [
    {
        "slug": "politics",
        "title": "السياسة والحكومة",
        "icon": "🏛️",
        "accent": "bg-blue-600",
        "category_names": ["محلي", "أخبار"],
        "keywords": ["مجلس القيادة", "العليمي", "رئيس الوزراء", "الحكومة", "وزير", "وزارة", "البرلمان", "سفير", "المبعوث", "الأمم المتحدة", "الشرعية", "الانتقالي", "مشاورات", "الرياض", "جنيف", "قرار جمهوري"],
    },
    {
        "slug": "conflict",
        "title": "التطورات العسكرية والأمنية",
        "icon": "🛡️",
        "accent": "bg-red-600",
        "category_names": ["عاجل", "محلي"],
        "keywords": ["القوات المسلحة", "غارات", "قصف", "استهداف", "صاروخ", "طيران", "معارك", "جبهة", "جبهات", "الأمن", "شرطة", "انفجار", "مطار عدن", "البحر الأحمر", "باب المندب", "الحوثي", "مليشيا", "حصار"],
    },
    {
        "slug": "local",
        "title": "الشأن المحلي والمحافظات",
        "icon": "📍",
        "accent": "bg-emerald-600",
        "category_names": ["محلي"],
        "keywords": ["صنعاء", "عدن", "تعز", "مأرب", "حضرموت", "الحديدة", "شبوة", "صعدة", "المكلا", "الضالع", "لحج", "أبين", "المهرة", "سقطرى", "البيضاء", "الجوف", "ذمار", "إب", "حجة", "محافظ", "مديرية"],
    },
    {
        "slug": "economy",
        "title": "الاقتصاد وأسعار الصرف",
        "icon": "📈",
        "accent": "bg-amber-500",
        "category_names": ["اقتصاد"],
        "keywords": ["صرف", "الريال", "الدولار", "البنك المركزي", "أسعار الذهب", "سعر الذهب", "جرام الذهب", "النفط", "الوقود", "التجارة", "الجمارك", "الضرائب", "رواتب", "موازنة", "اقتصاد", "العملات"],
    },
    {
        "slug": "reports",
        "title": "تقارير وتحليلات",
        "icon": "📋",
        "accent": "bg-indigo-600",
        "category_names": ["تقارير", "بانوراما", "حصاد الصحافة"],
        "keywords": ["تقرير", "تحقيق", "دراسة", "مركز أبعاد", "مركز صنعاء", "هيومن رايتس", "قراءة في", "ملف"],
    },
    {
        "slug": "opinion",
        "title": "مقالات وآراء",
        "icon": "✍️",
        "accent": "bg-purple-600",
        "category_names": ["آراء", "كتاب من اليمن"],
        "keywords": ["بقلم", "مقال", "وجهة نظر", "رأي", "يكتب", "كتب:", "بين مطرقة", "ما وراء", "لماذا"],
    },
    {
        "slug": "sports",
        "title": "الرياضة",
        "icon": "⚽",
        "accent": "bg-green-600",
        "category_names": ["رياضة"],
        "keywords": ["منتخب", "كأس الخليج", "كأس العالم", "بطولة", "مباراة", "دوري", "نادي", "كرة القدم", "تأهل", "أولمبياد"],
    },
    {
        "slug": "health_society",
        "title": "الصحة والمجتمع وحقوق الإنسان",
        "icon": "⚕️",
        "accent": "bg-teal-600",
        "category_names": ["صحة", "مجتمع", "المرأة"],
        "keywords": ["صحة", "مستشفى", "الصحة العالمية", "اليونيسيف", "المرأة", "الطفل", "حقوق الإنسان", "الأوبئة", "تعليم", "جامعة", "مدارس", "إغاثة", "نازحين"],
    },
    {
        "slug": "culture",
        "title": "الثقافة والفن والتراث",
        "icon": "🎭",
        "accent": "bg-pink-600",
        "category_names": ["ثقافة وفن"],
        "keywords": ["ثقافة", "فنان", "تراث", "شاعر", "قصيدة", "رواية", "مسرح", "معرض", "سينما", "الدسمال", "إبداع", "أدب"],
    },
    {
        "slug": "technology",
        "title": "التكنولوجيا والعلوم",
        "icon": "💻",
        "accent": "bg-cyan-600",
        "category_names": ["تكنولوجيا"],
        "keywords": ["تكنولوجيا", "الذكاء الاصطناعي", "آيفون", "أندرويد", "تطبيق", "هاتف", "ستارلينك", "الإنترنت", "اتصالات", "رقمي", "إلكترونية"],
    },
    {
        "slug": "arab_intl",
        "title": "أخبار عربية ودولية",
        "icon": "🌍",
        "accent": "bg-slate-600",
        "category_names": ["عربي", "دولي", "ترجمة", "ترجمات"],
        "keywords": ["فلسطين", "غزة", "لبنان", "السعودية", "مصر", "السودان", "روسيا", "واشنطن", "الأمم المتحدة", "مجلس الأمن", "إيران", "أوروبا"],
    },
]


def _section_three_tier_sort_key(post: Post, source_weights: dict[int, dict], now=None) -> tuple:
    """
    Sorts articles inside each section strictly by:
    1. Cluster velocity (topic_size with freshness decay if > 1, else 0)
    2. Number of reads (post_views_count)
    3. Reputation of the source (most relevant to Yemeni news)
    4. Recency (published_at)
    """
    if now is None:
        now = timezone.now()
    age_hours = max(0.0, (now - post.published_at).total_seconds() / 3600.0)
    recency_decay = 1.0 / (1.0 + (age_hours / 4.0) ** 1.5)
    raw_cluster_size = post.topic.topic_size if (post.topic_id and post.topic and post.topic.topic_size > 1) else 0
    cluster_score = (raw_cluster_size * 10.0) * recency_decay
    reads = post.post_views_count or 0
    src_info = source_weights.get(post.source_id, {})
    src_reputation = src_info.get("total_weight", 0.0) if isinstance(src_info, dict) else float(src_info or 0.0)
    return (cluster_score, reads, src_reputation, post.published_at)


def get_homepage_thematic_sections(source_weights: dict[int, dict], exclude_post_ids: set[int]) -> list[dict]:
    """
    Builds the 11 main thematic sections on the homepage strictly within the last 12 hours,
    each sorted by:
    Cluster Velocity (with freshness decay) -> Number of Reads -> Source Yemen Reputation.
    """
    now = timezone.now()
    pool = list(
        Post.objects.filter(
            state=Post.State.APPROVED,
            published_at__gte=now - timedelta(hours=12),
        )
        .select_related("source", "topic")
        .prefetch_related("categories")
        .order_by("-published_at")[:1500]
    )

    # Fallback to 48 hours only if the whole pool is sparse (< 50 items)
    if len(pool) < 50:
        pool = list(
            Post.objects.filter(
                state=Post.State.APPROVED,
                published_at__gte=now - timedelta(days=2),
            )
            .select_related("source", "topic")
            .prefetch_related("categories")
            .order_by("-published_at")[:1500]
        )

    # Map topic_id -> fallback image_url from sibling posts
    topic_images: dict[int, str] = {}
    for p in pool:
        if p.topic_id and p.image_url and p.image_url.startswith("http") and p.topic_id not in topic_images:
            topic_images[p.topic_id] = p.image_url

    cat_name_to_id = {c.name: c.id for c in Category.objects.all()}
    sections_output = []
    global_used_post_ids = set(exclude_post_ids)
    global_used_topics = set()
    for p in pool:
        if p.id in global_used_post_ids and p.topic_id:
            global_used_topics.add(p.topic_id)

    for spec in THEMATIC_SECTIONS_SPEC:
        cat_set = set(spec["category_names"])
        kw_list = spec["keywords"]
        primary_cat_id = next((cat_name_to_id[cn] for cn in spec["category_names"] if cn in cat_name_to_id), None)

        matched = []
        for p in pool:
            if p.id in global_used_post_ids:
                continue
            if p.topic_id and p.topic_id in global_used_topics:
                continue
            post_cat_names = {c.name for c in p.categories.all()}
            title_text = p.title or ""

            # Prevent sports articles from leaking into non-sports sections
            if spec["slug"] != "sports" and "رياضة" in post_cat_names:
                continue

            # For topical sections like Sports, Tech, Culture, Opinion, require category match or strong keyword
            if spec["slug"] in ("sports", "culture", "technology", "opinion"):
                if not (post_cat_names.intersection(cat_set) or any(kw in title_text for kw in kw_list)):
                    continue
            elif spec["slug"] in ("politics", "conflict", "local"):
                if not is_yemen_relevant(p):
                    continue
                if not any(kw in title_text for kw in kw_list):
                    continue
            else:
                if not (post_cat_names.intersection(cat_set) or any(kw in title_text for kw in kw_list)):
                    continue

            matched.append(p)

        # Sort by 3-tier rule: 1. Cluster Velocity (freshness-decayed) -> 2. Reads -> 3. Source Yemen Reputation
        matched.sort(key=lambda p: _section_three_tier_sort_key(p, source_weights, now=now), reverse=True)

        # Deduplicate by topic_id and title prefix
        seen_topics = set()
        seen_titles = set()
        section_posts = []
        for p in matched:
            if p.topic_id and p.topic_id in seen_topics:
                continue
            t_key = (p.title or "").strip()[:45]
            if t_key in seen_titles:
                continue
            if p.topic_id:
                seen_topics.add(p.topic_id)
                global_used_topics.add(p.topic_id)
                if not p.image_url and p.topic_id in topic_images:
                    p.image_url = topic_images[p.topic_id]
            seen_titles.add(t_key)
            global_used_post_ids.add(p.id)
            section_posts.append(p)
            if len(section_posts) >= 6:
                break

        if section_posts:
            sections_output.append({
                "slug": spec["slug"],
                "title": spec["title"],
                "icon": spec["icon"],
                "accent": spec["accent"],
                "category_id": primary_cat_id,
                "posts": section_posts,
            })

    return sections_output


def get_portal_stats() -> dict:
    """
    Returns cached statistics for news items, clusters, and active sources
    over the last 24 hours, last 7 days, and in total.
    """
    cached = cache.get("portal_stats_v1")
    if cached is not None:
        return cached

    now = timezone.now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_7d = now - timedelta(days=7)

    agg_7d = Post.objects.filter(
        state=Post.State.APPROVED,
        published_at__gte=cutoff_7d,
    ).aggregate(
        posts_24h=Count("id", filter=Q(published_at__gte=cutoff_24h)),
        clusters_24h=Count("topic_id", distinct=True, filter=Q(published_at__gte=cutoff_24h, topic__topic_size__gt=1)),
        sources_24h=Count("source_id", distinct=True, filter=Q(published_at__gte=cutoff_24h)),
        posts_7d=Count("id"),
        clusters_7d=Count("topic_id", distinct=True, filter=Q(topic__topic_size__gt=1)),
        sources_7d=Count("source_id", distinct=True),
    )

    totals = cache.get("portal_stats_totals_v1")
    if totals is None:
        totals = {
            "posts_total": Post.objects.filter(state=Post.State.APPROVED).count(),
            "clusters_total": Topic.objects.filter(topic_size__gt=1).count(),
            "sources_total": Source.objects.filter(
                approve_state=Source.ApproveState.APPROVED,
                state=Source.State.VALID,
            ).count(),
        }
        cache.set("portal_stats_totals_v1", totals, timeout=21600)

    stats = {
        "posts_24h": agg_7d.get("posts_24h") or 0,
        "clusters_24h": agg_7d.get("clusters_24h") or 0,
        "sources_24h": agg_7d.get("sources_24h") or 0,
        "posts_7d": agg_7d.get("posts_7d") or 0,
        "clusters_7d": agg_7d.get("clusters_7d") or 0,
        "sources_7d": agg_7d.get("sources_7d") or 0,
        **totals,
    }
    cache.set("portal_stats_v1", stats, timeout=900)
    return stats


def get_homepage_portal_widgets() -> dict:
    """
    Returns Yemen Portal homepage blocks cached in Redis:
    - hero_post: #1 Top Clustered Story
    - top_clusters: Next 6 Top Clustered Stories under 'أبرز الأخبار'
    - readers_picks: Next 3 stories under 'اختيارات القراء'
    - thematic_sections: 11 attractive thematic sections sorted by Cluster Size -> Reads -> Source Reputation
    - latest_sidebar_posts: Latest 18 chronological posts for the 'آخر الأخبار' sidebar column
    - top_sources: Top 12 active Yemen-focused sources
    - portal_stats: 24h / 7d / Total counts of news items, clusters, and active sources
    """
    cached = cache.get("portal_homepage_widgets_v6")
    if cached:
        return cached

    now = timezone.now()
    source_weights = get_source_activity_weights()
    base_qs = (
        Post.objects.filter(state=Post.State.APPROVED)
        .select_related("source", "topic")
        .prefetch_related("categories")
    )

    ranked_yemen = get_ranked_yemen_posts(hours=4, limit=30)

    # Sort top clustered stories by velocity (cluster size * freshness decay) -> reads -> source reputation
    def cluster_velocity_score(p):
        age_hours = max(0.0, (now - p.published_at).total_seconds() / 3600.0)
        decay = 1.0 / (1.0 + (age_hours / 3.0) ** 1.8)
        raw_size = p.topic.topic_size if (p.topic and "أسعار صرف" not in (p.title or "")) else min(p.topic.topic_size, 4)
        v_score = (raw_size * 15.0) * decay
        return (
            v_score,
            p.post_views_count or 0,
            source_weights.get(p.source_id, {}).get("total_weight", 0.0),
            p.published_at,
        )

    clustered_candidates = [
        p for p in ranked_yemen
        if p.topic_id and p.topic and p.topic.topic_size > 1
    ]
    clustered_candidates.sort(
        key=cluster_velocity_score,
        reverse=True,
    )

    if len(clustered_candidates) < 7:
        used_c_ids = {p.id for p in clustered_candidates}
        for p in ranked_yemen:
            if p.id not in used_c_ids:
                clustered_candidates.append(p)
                if len(clustered_candidates) >= 7:
                    break

    # 1. Hero Post + 6 More Top Clustered Stories under 'أبرز الأخبار' (7 items total!)
    hero_post = clustered_candidates[0] if clustered_candidates else base_qs.order_by("-published_at").first()
    top_clusters = clustered_candidates[1:7]

    used_top_ids = {hero_post.id} if hero_post else set()
    used_top_ids.update(p.id for p in top_clusters)

    # 2. Readers' Picks (اختيارات القراء)
    readers_picks = [p for p in ranked_yemen if p.id not in used_top_ids][:3]
    if not readers_picks and len(ranked_yemen) > 1:
        readers_picks = ranked_yemen[1:4]

    # 3. Latest Chronological News for Sidebar ('آخر الأخبار' column replacing 'مقالات وآراء' in sidebar)
    latest_sidebar_posts = list(
        base_qs.order_by("-published_at")[:18]
    )

    # 4. 11 Main Thematic Sections for Main Body (sorted by Cluster Size -> Reads -> Source Reputation)
    section_excludes = used_top_ids if len(ranked_yemen) > 10 else ({hero_post.id} if hero_post else set())
    thematic_sections = get_homepage_thematic_sections(
        source_weights=source_weights,
        exclude_post_ids=section_excludes,
    )

    # Keep opinion_posts for subpages that reference it
    opinion_sec = next((s["posts"] for s in thematic_sections if s["slug"] == "opinion"), [])

    # 5. Top Sources Directory (دليل المواقع / المصادر النشطة) - weighted by on-the-fly Yemen Focus Ratio
    top_sources = cache.get("portal_top_sources_v3")
    if not top_sources:
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
        "top_clusters": top_clusters,
        "readers_picks": readers_picks,
        "latest_sidebar_posts": latest_sidebar_posts,
        "thematic_sections": thematic_sections,
        "opinion_posts": opinion_sec,
        "top_sources": top_sources,
        "portal_stats": get_portal_stats(),
    }
    cache.set("portal_homepage_widgets_v6", data, timeout=600)
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
