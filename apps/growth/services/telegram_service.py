import json
import logging
import urllib.request
import urllib.error
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from apps.posts.services.portal_services import get_exchange_rates
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

    rates_data = get_exchange_rates()
    sanaa_list = rates_data.get('sanaa', [])
    aden_list = rates_data.get('aden', [])

    def get_rate(items, code):
        for r in items:
            if getattr(r, 'currency_code', '') == code:
                return r
        return None

    sanaa_usd = get_rate(sanaa_list, 'USD')
    sanaa_sar = get_rate(sanaa_list, 'SAR')
    aden_usd = get_rate(aden_list, 'USD')
    aden_sar = get_rate(aden_list, 'SAR')

    date_str = now.strftime('%Y-%m-%d')

    msg_lines = [
        "📊 <b>نشرة أسعار الصرف في اليمن — يمن بورتال</b>",
        f"🗓 <i>تحديث مباشر: {date_str}</i>",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "📍 <b>أسعار الصرف في عدن:</b>",
    ]

    if aden_usd:
        msg_lines.append(f"🇺🇸 <b>الدولار الأمريكي:</b> شراء: {aden_usd.buy_price:,.0f} | بيع: {aden_usd.sell_price:,.0f} ريال")
    if aden_sar:
        msg_lines.append(f"🇸🇦 <b>الريال السعودي:</b> شراء: {aden_sar.buy_price:,.0f} | بيع: {aden_sar.sell_price:,.0f} ريال")

    msg_lines.extend([
        "",
        "────────────────────",
        "📍 <b>أسعار الصرف في صنعاء:</b>",
    ])

    if sanaa_usd:
        msg_lines.append(f"🇺🇸 <b>الدولار الأمريكي:</b> شراء: {sanaa_usd.buy_price:,.0f} | بيع: {sanaa_usd.sell_price:,.0f} ريال")
    if sanaa_sar:
        msg_lines.append(f"🇸🇦 <b>الريال السعودي:</b> شراء: {sanaa_sar.buy_price:,.1f} | بيع: {sanaa_sar.sell_price:,.1f} ريال")

    msg_lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🔗 <a href=\"https://yemenportal.net/posts/currency/?utm_source=telegram&utm_medium=channel&utm_campaign=morning_rates\">تابع التحديث اللحظي لأسعار الصرف والذهب على الموقع</a>",
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

    # Get topics already successfully published to Telegram
    already_published_ids = set(
        PublishedChannelPost.objects.filter(
            channel=PublishedChannelPost.Channel.TELEGRAM,
            post_type=PublishedChannelPost.PostType.HOT_CLUSTER,
            status=PublishedChannelPost.Status.PUBLISHED,
            topic__isnull=False
        ).values_list('topic_id', flat=True)
    )

    candidate_topics = (
        Topic.objects.filter(
            Q(created_at__gte=cutoff) | Q(updated_at__gte=cutoff),
            topic_size__gte=min_sources
        )
        .exclude(id__in=already_published_ids)
        .select_related('main_post', 'main_post__source')
        .order_by('-topic_size', '-updated_at')[:max_per_run]
    )

    results = []

    for topic in candidate_topics:
        lead_post = topic.main_post or topic.posts.order_by('-published_at').first()
        if not lead_post:
            continue

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
            f"🔥 <b>تغطية مجمعة ({cluster_size} مصادر إخبارية):</b>",
            "",
            f"<b>{title}</b>",
            "",
            "📌 <b>أبرز المصادر المواكبة للحدث:</b>",
            f"<i>{sources_str}</i>",
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "📊 <b>قارن بين روايات وتغطيات كافة المصادر في صفحة واحدة:</b>",
            f"👉 <a href=\"{utm_link}\">اضغط هنا لقراءة ومقارنة التغطية الكاملة على يمن بورتال</a>",
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

    return results
