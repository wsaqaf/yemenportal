import json
import logging
import urllib.request
import urllib.error
import time
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from apps.posts.services.portal_services import (
    get_exchange_rates,
    is_eligible_for_top_news,
    has_genuine_yemen_focus,
)
from apps.posts.models import Topic
from apps.growth.models import PublishedChannelPost

logger = logging.getLogger(__name__)


def send_telegram_message(text: str, parse_mode: str = 'HTML', disable_web_page_preview: bool = False) -> dict:
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


def publish_next_hot_cluster(min_sources: int = 3, max_per_run: int = 1, hours: int = 72) -> list[dict]:
    """
    Finds recent news clusters with at least `min_sources` distinct sources
    that have not been published to Telegram yet, and broadcasts them.
    """
    cutoff = timezone.now() - timedelta(hours=hours)

    # Routine phrases to skip in news clusters (handled separately or low editorial value)
    routine_phrases = ['أسعار الصرف', 'صرف العملات', 'أسعار العملات', 'حالة الطقس', 'درجات الحرارة']

    # Get topics already successfully published to Telegram
    already_published_ids = set(
        PublishedChannelPost.objects.filter(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type=PublishedChannelPost.PostType.HOT_CLUSTER,
            status=PublishedChannelPost.Status.PUBLISHED,
            topic__isnull=False
        ).values_list('topic_id', flat=True)
    )

    raw_candidates = list(
        Topic.objects.filter(
            Q(created_at__gte=cutoff) | Q(updated_at__gte=cutoff),
            topic_size__gte=min_sources
        )
        .exclude(id__in=already_published_ids)
        .select_related('main_post', 'main_post__source')
        .order_by('-created_at', '-topic_size')[:max_per_run * 25]
    )

    yemen_candidates = []
    major_intl_candidates = []

    for topic in raw_candidates:
        lead_post = topic.main_post or topic.posts.order_by('-published_at').first()
        if not lead_post or not lead_post.title:
            continue

        title = lead_post.title.strip()
        # Skip routine exchange rates or weather summaries from news cluster feed
        if any(phrase in title for phrase in routine_phrases):
            continue

        # Strict editorial gatekeeper: must be genuine Yemen news or major geopolitical event
        if not is_eligible_for_top_news(lead_post):
            continue

        # Prioritize genuine Yemen focus; major international events (US elections, regional wars) secondary
        if has_genuine_yemen_focus(lead_post):
            yemen_candidates.append((topic, lead_post))
        else:
            major_intl_candidates.append((topic, lead_post))

    eligible_candidates = yemen_candidates + major_intl_candidates

    results = []

    for topic, lead_post in eligible_candidates:
        if len(results) >= max_per_run:
            break

        title = lead_post.title.strip()
        cluster_size = topic.topic_size

        # Extract distinct top source names
        sources = list(
            topic.posts.filter(source__isnull=False)
            .values_list('source__name', flat=True)
            .distinct()[:5]
        )
        sources_str = " • ".join(sources) if sources else "مصادر متعددة"

        utm_link = f"https://yemenportal.net/posts/topic/{topic.id}/?utm_source=telegram&utm_medium=channel&utm_campaign=hot_cluster"

        msg_lines = [
            f"<a href=\"{utm_link}\"><b>{title}</b></a>",
            "",
            f"📌 <b>المصادر ({cluster_size}):</b> {sources_str}",
        ]

        message_text = "\n".join(msg_lines)
        res = send_telegram_message(message_text, disable_web_page_preview=False)

        status = PublishedChannelPost.Status.PUBLISHED if res.get('ok') else PublishedChannelPost.Status.FAILED
        msg_id = str(res.get('result', {}).get('message_id', ''))
        err = "" if res.get('ok') else str(res.get('description', res.get('error', '')))

        PublishedChannelPost.objects.create(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type=PublishedChannelPost.PostType.HOT_CLUSTER,
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
            'status': 'published' if res.get('ok') else 'failed',
            'message_id': msg_id,
            'error': err,
        })

        if len(results) < max_per_run:
            time.sleep(1.5)

    return results
