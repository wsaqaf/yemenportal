import json
import logging
import urllib.request
import urllib.error
import time
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from apps.posts.services.portal_services import (
    BREAKING_KEYWORDS,
    get_exchange_rates,
    is_eligible_for_top_news,
    has_genuine_yemen_focus,
)
from apps.posts.models import Topic
from apps.growth.models import PublishedChannelPost

logger = logging.getLogger(__name__)

# Balanced high-signal Telegram defaults: urgent & important clusters (~12-20/day vs ~94/day previously)
DEFAULT_MAJOR_MIN_SOURCES = 6
DEFAULT_URGENT_MIN_SOURCES = 4
DEFAULT_INTL_MIN_SOURCES = 8
DEFAULT_URGENT_CAP_BYPASS_SOURCES = 6
DEFAULT_LOOKBACK_HOURS = 12
DEFAULT_COOLDOWN_MINUTES = 45
DEFAULT_URGENT_COOLDOWN_MINUTES = 15
DEFAULT_MAX_DAILY_CLUSTERS = 20

# Yemen time (UTC+3) quiet hours for non-urgent notifications (23:00 - 07:00)
QUIET_HOURS_YEMEN_START = 23
QUIET_HOURS_YEMEN_END = 7

TELEGRAM_URGENT_KEYWORDS = tuple(set(BREAKING_KEYWORDS) | {
    'عاجل', 'غارة', 'غارات', 'انفجار', 'استهداف', 'قصف', 'مقتل', 'اغتيال',
    'تحذير', 'إخلاء', 'كارثة', 'زلزال', 'انهيار', 'قرار جمهوري', 'قرارات جمهورية',
    'صاروخ', 'صواريخ', 'مسيرة', 'مسيّرة', 'مسيرتين', 'مقذوف', 'اعتراض', 'تدمير',
    'هجوم', 'معارك', 'اشتباكات', 'حالة طوارئ', 'إغلاق', 'عقوبات',
})

TELEGRAM_SKIP_PHRASES = (
    'أسعار الصرف', 'صرف العملات', 'أسعار العملات', 'حالة الطقس', 'درجات الحرارة',
    'كشف توزيع الغاز', 'دوري أبطال', 'الدوري الإنجليزي', 'الدوري الإسباني',
    'الدوري السعودي', 'كأس العالم', 'كأس أمم', 'كرة القدم', 'أتلتيكو مدريد',
    'ريال مدريد', 'برشلونة', 'ليفربول', 'مانشستر', 'محمد صلاح',
)


def is_urgent_cluster(title: str) -> bool:
    """Returns True if the headline indicates an urgent/breaking high-impact development."""
    if not title:
        return False
    return any(kw in title for kw in TELEGRAM_URGENT_KEYWORDS)


def _yemen_day_start(now=None):
    """Returns UTC datetime corresponding to 00:00 today in Yemen time (UTC+3)."""
    now = now or timezone.now()
    yemen_now = now + timedelta(hours=3)
    yemen_midnight = yemen_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return yemen_midnight - timedelta(hours=3)


def _is_yemen_quiet_hours(now=None) -> bool:
    """Returns True between 23:00 and 07:00 Yemen time (UTC+3)."""
    now = now or timezone.now()
    yemen_hour = (now.hour + 3) % 24
    return yemen_hour >= QUIET_HOURS_YEMEN_START or yemen_hour < QUIET_HOURS_YEMEN_END


def send_telegram_message(
    text: str,
    parse_mode: str = 'HTML',
    disable_web_page_preview: bool = False,
    disable_notification: bool = False,
) -> dict:
    """
    Sends a message to the configured Telegram channel using Telegram Bot API.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    channel_id = getattr(settings, 'TELEGRAM_CHANNEL_ID', '')

    if not token or not channel_id:
        logger.warning("Telegram Bot Token or Channel ID is not configured.")
        return {'ok': False, 'error': 'Missing credentials'}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': channel_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        logger.error(f"Telegram API HTTP error {e.code}: {err_body}")
        return {'ok': False, 'error_code': e.code, 'description': err_body}
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return {'ok': False, 'error': str(e)}


def publish_morning_exchange_rates(force: bool = False) -> dict:
    """
    Publishes the daily morning exchange rates in a distinct, styled box.
    Avoids sending duplicate daily updates unless force=True.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if not force:
        already_published = PublishedChannelPost.objects.filter(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type=PublishedChannelPost.PostType.EXCHANGE_RATES,
            created_at__gte=today_start,
            status=PublishedChannelPost.Status.PUBLISHED
        ).exists()
        if already_published:
            return {'status': 'skipped', 'reason': 'already published today'}

    from apps.posts.services.portal_services import update_exchange_rates_from_kuraimi
    rates_data = get_exchange_rates()
    latest_update = rates_data.get('updated_at')
    if not latest_update or (now - latest_update).total_seconds() > 6 * 3600:
        try:
            if update_exchange_rates_from_kuraimi() > 0:
                rates_data = get_exchange_rates()
        except Exception:
            pass

    regions = rates_data.get('regions', [])

    def fmt_price(val):
        text = f"{val:,.1f}"
        return text[:-2] if text.endswith('.0') else text

    def rates_signature(items):
        return tuple(
            (r.currency_code, fmt_price(r.buy_price), fmt_price(r.sell_price))
            for r in items
        )

    def format_rate_lines(items):
        labels = {
            'USD': '🇺🇸 <b>الدولار الأمريكي:</b>',
            'SAR': '🇸🇦 <b>الريال السعودي:</b>',
            'AED': '🇦🇪 <b>الدرهم الإماراتي:</b>',
        }
        lines = []
        for r in items:
            lbl = labels.get(r.currency_code, f"💱 <b>{r.get_currency_code_display()}:</b>")
            lines.append(f"{lbl} شراء: {fmt_price(r.buy_price)} | بيع: {fmt_price(r.sell_price)} ريال")
        return lines

    # Group regions sharing identical rates to keep the bulletin concise while
    # automatically surfacing any regional divergence if Kuraimi publishes one.
    grouped = []
    sig_to_group = {}
    for reg in regions:
        reg_rates = reg.get('rates', [])
        if not reg_rates:
            continue
        sig = rates_signature(reg_rates)
        if sig in sig_to_group:
            sig_to_group[sig]['names'].append(reg['name'])
        else:
            entry = {'names': [reg['name']], 'rates': reg_rates}
            sig_to_group[sig] = entry
            grouped.append(entry)

    date_str = now.strftime('%Y-%m-%d')

    msg_lines = [
        "📊 <b>نشرة أسعار الصرف في اليمن — يمن بورتال</b>",
        f"🗓 <i>تحديث مباشر: {date_str}</i>",
        "━━━━━━━━━━━━━━━━━━━━",
    ]

    for idx, grp in enumerate(grouped):
        if idx > 0:
            msg_lines.append("")
            msg_lines.append("────────────────────")
        else:
            msg_lines.append("")
        region_title = "، ".join(grp['names'])
        msg_lines.append(f"📍 <b>أسعار الصرف في {region_title}:</b>")
        msg_lines.extend(format_rate_lines(grp['rates']))

    msg_lines.extend([
        "",
        "🏦 <i>المصدر: بنك الكريمي للتمويل الأصغر الإسلامي</i>",
        "━━━━━━━━━━━━━━━━━━━━",
        "🔗 <a href=\"https://yemenportal.net/posts/currency/?utm_source=telegram&utm_medium=channel&utm_campaign=morning_rates\">تابع التحديث اللحظي لأسعار الصرف والمحافظات على الموقع</a>",
    ])

    message_text = "\n".join(msg_lines)
    res = send_telegram_message(message_text, disable_web_page_preview=False)

    status = PublishedChannelPost.Status.PUBLISHED if res.get('ok') else PublishedChannelPost.Status.FAILED
    msg_id = str(res.get('result', {}).get('message_id', ''))
    err = "" if res.get('ok') else str(res.get('description', res.get('error', '')))

    PublishedChannelPost.objects.create(
        channel=PublishedChannelPost.Channel.TELEGRAM,
        post_type=PublishedChannelPost.PostType.EXCHANGE_RATES,
        external_message_id=msg_id,
        message_text=message_text,
        status=status,
        error_message=err,
    )

    return {'status': 'published' if res.get('ok') else 'failed', 'message_id': msg_id, 'error': err}


def publish_next_hot_cluster(
    min_sources: int = DEFAULT_MAJOR_MIN_SOURCES,
    max_per_run: int = 1,
    hours: int = DEFAULT_LOOKBACK_HOURS,
    urgent_min_sources: int | None = None,
    cooldown_minutes: int = DEFAULT_COOLDOWN_MINUTES,
    urgent_cooldown_minutes: int = DEFAULT_URGENT_COOLDOWN_MINUTES,
    max_daily_posts: int = DEFAULT_MAX_DAILY_CLUSTERS,
    respect_limits: bool = True,
) -> list[dict]:
    """
    Finds recent urgent or highly important news clusters covered by enough
    distinct sources and broadcasts them to Telegram with pacing controls:
    - Major Yemen clusters: >= `min_sources` distinct sources (default: 8)
    - Urgent/breaking Yemen clusters: >= `urgent_min_sources` distinct sources (default: 5)
    - Major regional/international clusters: higher threshold (>= max(10, min_sources + 2), or >= min_sources if urgent)
    - Enforces daily cap (`max_daily_posts`) and cooldown between notifications (`cooldown_minutes` / `urgent_cooldown_minutes`)
    - Delivers non-urgent major clusters silently during Yemen night hours (23:00-07:00 UTC+3)
    """
    now = timezone.now()
    cutoff = now - timedelta(hours=hours)
    effective_urgent_min = (
        min(DEFAULT_URGENT_MIN_SOURCES, min_sources)
        if urgent_min_sources is None
        else min(urgent_min_sources, min_sources)
    )
    intl_major_min = max(DEFAULT_INTL_MIN_SOURCES, min_sources + 2)

    cluster_post_types = [
        PublishedChannelPost.PostType.HOT_CLUSTER,
        PublishedChannelPost.PostType.BREAKING,
    ]

    only_urgent = False
    daily_cap_reached = False
    if respect_limits:
        day_start = _yemen_day_start(now)
        today_qs = PublishedChannelPost.objects.filter(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type__in=cluster_post_types,
            status=PublishedChannelPost.Status.PUBLISHED,
            created_at__gte=day_start,
        )
        if max_daily_posts and today_qs.count() >= max_daily_posts:
            daily_cap_reached = True
            only_urgent = True
            logger.info(
                "Telegram daily cluster cap (%s/day) reached; only major breaking alerts (>= %s sources) allowed.",
                max_daily_posts,
                DEFAULT_URGENT_CAP_BYPASS_SOURCES,
            )

        last_published = (
            PublishedChannelPost.objects.filter(
                channel=PublishedChannelPost.Channel.TELEGRAM,
                post_type__in=cluster_post_types,
                status=PublishedChannelPost.Status.PUBLISHED,
            )
            .order_by('-created_at')
            .first()
        )
        if last_published:
            elapsed_minutes = (now - last_published.created_at).total_seconds() / 60.0
            if elapsed_minutes < urgent_cooldown_minutes:
                logger.info(
                    "Telegram urgent cooldown active (%.1fm < %sm); skipping broadcast.",
                    elapsed_minutes,
                    urgent_cooldown_minutes,
                )
                return []
            if elapsed_minutes < cooldown_minutes:
                only_urgent = True

    # Get topics already successfully published to Telegram
    already_published_ids = set(
        PublishedChannelPost.objects.filter(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type__in=cluster_post_types,
            status=PublishedChannelPost.Status.PUBLISHED,
            topic__isnull=False,
        ).values_list('topic_id', flat=True)
    )

    raw_candidates = list(
        Topic.objects.filter(
            Q(created_at__gte=cutoff) | Q(updated_at__gte=cutoff),
            topic_size__gte=effective_urgent_min,
        )
        .exclude(id__in=already_published_ids)
        .annotate(distinct_sources=Count('posts__source', distinct=True))
        .filter(distinct_sources__gte=effective_urgent_min)
        .select_related('main_post', 'main_post__source')
        .order_by('-distinct_sources', '-topic_size', '-created_at')[:max(max_per_run * 40, 40)]
    )

    qualified_candidates = []

    for topic in raw_candidates:
        lead_post = topic.main_post or topic.posts.order_by('-published_at').first()
        if not lead_post or not lead_post.title:
            continue

        title = lead_post.title.strip()
        if any(phrase in title for phrase in TELEGRAM_SKIP_PHRASES):
            continue

        # Strict editorial gatekeeper: must be genuine Yemen news or major geopolitical event
        if not is_eligible_for_top_news(lead_post):
            continue

        distinct_sources = topic.distinct_sources or 0
        urgent = is_urgent_cluster(title)
        is_yemen = has_genuine_yemen_focus(lead_post)

        if only_urgent and not urgent:
            continue

        if daily_cap_reached and distinct_sources < DEFAULT_URGENT_CAP_BYPASS_SOURCES:
            continue

        if is_yemen:
            qualifies = distinct_sources >= min_sources or (urgent and distinct_sources >= effective_urgent_min)
        else:
            qualifies = distinct_sources >= intl_major_min or (urgent and distinct_sources >= min_sources)

        if not qualifies:
            continue

        priority_tier = 0 if (is_yemen and urgent) else (1 if is_yemen else 2)
        qualified_candidates.append((priority_tier, -distinct_sources, -topic.topic_size, topic, lead_post, distinct_sources, urgent))

    qualified_candidates.sort(key=lambda item: (item[0], item[1], item[2]))

    results = []
    quiet_hours = _is_yemen_quiet_hours(now)

    for _, _, _, topic, lead_post, distinct_sources, urgent in qualified_candidates:
        if len(results) >= max_per_run:
            break

        title = lead_post.title.strip()

        # Extract distinct top source names
        sources = list(
            topic.posts.filter(source__isnull=False)
            .values_list('source__name', flat=True)
            .distinct()[:5]
        )
        sources_str = " • ".join(sources) if sources else "مصادر متعددة"

        utm_campaign = "breaking_cluster" if urgent else "hot_cluster"
        utm_link = f"https://yemenportal.net/posts/topic/{topic.id}/?utm_source=telegram&utm_medium=channel&utm_campaign={utm_campaign}"

        headline_prefix = "🔴 <b>عاجل |</b> " if (urgent and "عاجل" not in title) else ""
        msg_lines = [
            f"{headline_prefix}<a href=\"{utm_link}\"><b>{title}</b></a>",
            "",
            f"📌 <b>المصادر ({distinct_sources}):</b> {sources_str}",
        ]

        message_text = "\n".join(msg_lines)
        disable_notification = quiet_hours and not urgent
        res = send_telegram_message(
            message_text,
            disable_web_page_preview=False,
            disable_notification=disable_notification,
        )

        status = PublishedChannelPost.Status.PUBLISHED if res.get('ok') else PublishedChannelPost.Status.FAILED
        msg_id = str(res.get('result', {}).get('message_id', ''))
        err = "" if res.get('ok') else str(res.get('description', res.get('error', '')))
        post_type = (
            PublishedChannelPost.PostType.BREAKING
            if urgent
            else PublishedChannelPost.PostType.HOT_CLUSTER
        )

        PublishedChannelPost.objects.create(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type=post_type,
            topic=topic,
            post=lead_post,
            external_message_id=msg_id,
            message_text=message_text,
            status=status,
            error_message=err,
        )

        results.append({
            'topic_id': topic.id,
            'title': title,
            'distinct_sources': distinct_sources,
            'urgent': urgent,
            'silent': disable_notification,
            'status': 'published' if res.get('ok') else 'failed',
            'message_id': msg_id,
            'error': err,
        })

        if len(results) < max_per_run:
            time.sleep(1.5)

    return results
