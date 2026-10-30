import re
from urllib.parse import urlparse

# Yemeni geographic and political indicators
YEMEN_INDICATORS = [
    "اليمن", "يمني", "يمنية", "صنعاء", "عدن", "تعز", "مأرب", "حضرموت", "الحديدة",
    "إب", "ذمار", "صعدة", "حجة", "شبوة", "أبين", "لحج", "الضالع", "المهرة", "سقطرى",
    "البيضاء", "الجوف", "عمران", "المحويت", "ريمة", "رداع", "المكلا", "سيئون", "المخا",
    "عتق", "يافع", "ردفان", "الصبيحة", "الحوثي", "الحوثيين", "الانتقالي", "العليمي",
    "الزبيدي", "الشرعية", "سبأ", "الريال اليمني", "البنك المركزي اليمني", "درع الوطن",
    "العمالقة", "المقاومة الوطنية", "طارق صالح", "معين عبدالملك", "بن مبارك",
]

# Yemeni source name conventions & known brands
YEMEN_SOURCE_NAMES = [
    "يمن", "عدن", "تعز", "مأرب", "حضرموت", "المهرية", "بلقيس", "سبأ", "كريتر", "المصدر",
    "26 سبتمبر", "صنعاء", "يافع", "الصحوة", "الأمناء", "المشهد اليمني", "نيوزيمن",
    "2 ديسمبر", "الشارع", "أبين", "شبوة", "الحديدة", "لحج", "سقطرى", "المهرة", "الضالع",
    "المنتصف", "حشد", "برس", "عين اليمن", "براقش", "المسيلة", "السجل", "الأيام",
    "وكالة 2 ديسمبر", "الموقع بوست", "المشاهد", "خفر السواحل", "الخبر اليمني",
]

# Major international news agencies and global media in Arabic
INTERNATIONAL_DOMAINS = [
    "reuters.com", "bbc.co.uk", "bbc.com", "france24.com", "dw.com", "alhurra.com",
    "cnn.com", "rt.com", "sputniknews.com", "sputniknews.lat", "sputnikglobe.com",
    "independentarabia.com", "skynewsarabia.com", "euronews.com", "aa.com.tr",
    "aa.com", "apnews.com", "afp.com", "al-monitor.com", "middleeasteye.net",
    "theguardian.com", "nytimes.com", "washingtonpost.com", "bloomberg.com",
]

INTERNATIONAL_NAMES = [
    "رويترز", "بي بي سي", "فرانس 24", "دويتشه فيله", "الحرة", "سي إن إن", "سي ان ان",
    "روسيا اليوم", "سبوتنيك", "إندبندنت عربية", "سكاي نيوز", "يورونيوز", "الأناضول",
    "أسوشيتد برس", "فرانس برس", "مونت كارلو", "بلومبرغ",
]

# Arab regional country TLDs and known pan-Arab outlets
ARAB_COUNTRY_TLDS = [
    ".sa", ".ae", ".eg", ".qa", ".kw", ".om", ".bh", ".jo", ".lb", ".iq",
    ".sy", ".ps", ".sd", ".ly", ".tn", ".dz", ".ma",
]

ARAB_REGIONAL_NAMES = [
    "الجزيرة", "العربية", "الحدث", "الشرق الأوسط", "اليوم السابع", "المصري اليوم",
    "القدس العربي", "عكاظ", "الرياض", "الخليج", "البيان", "القبس", "النهار", "الشروق",
    "الدستور", "الأهرام", "البوابة نيوز", "العرب", "رأي اليوم", "إرم نيوز", "سبق",
    "الشرق للأخبار", "عربي 21", "عربي بوست", "العربي الجديد",
]


def _extract_domain(url: str) -> str:
    """Extracts a clean lowercase hostname without www. or port."""
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    try:
        host = urlparse(url).netloc.lower()
        host = re.sub(r":\d+$", "", host)
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def _host_matches(host: str, targets: list[str]) -> bool:
    return any(host == t or host.endswith("." + t) for t in targets)


def classify_source_scope(
    name: str = "",
    website_url: str = "",
    feed_url: str = "",
    brief_info: str = "",
    feed_entries: list = None,
    sample_posts: list = None,
) -> str:
    """
    Dynamically classifies a news source into one of three scopes:
    - 'موقع يمني' (Yemeni website)
    - 'موقع عربي' (Arab regional website)
    - 'موقع دولي' (International website)

    Uses a tiered evaluation:
    1. TLD and domain hostname matching
    2. Source brand name and descriptive keywords
    3. Content analysis of recent RSS feed entries or post titles
    """
    clean_name = (name or "").strip()
    desc = (brief_info or "").strip()
    web_host = _extract_domain(website_url)
    feed_host = _extract_domain(feed_url)
    all_text = f"{clean_name} {desc}"

    # 1. Check International domain matches
    if _host_matches(web_host, INTERNATIONAL_DOMAINS) or _host_matches(feed_host, INTERNATIONAL_DOMAINS):
        return "موقع دولي"

    # 2. Check International name indicators
    if any(k in clean_name for k in INTERNATIONAL_NAMES):
        return "موقع دولي"

    # 3. Check Yemeni TLD
    if web_host.endswith(".ye") or feed_host.endswith(".ye"):
        return "موقع يمني"

    # 4. Check explicit Yemeni naming conventions
    if any(k in clean_name for k in YEMEN_SOURCE_NAMES):
        return "موقع يمني"

    # 5. Check Arab regional country TLDs (.sa, .eg, .ae, etc.)
    if any(web_host.endswith(tld) or feed_host.endswith(tld) for tld in ARAB_COUNTRY_TLDS):
        return "موقع عربي"

    # 6. Check known Arab regional brand names
    if any(k in clean_name for k in ARAB_REGIONAL_NAMES):
        return "موقع عربي"

    # 7. Content analysis of RSS feed entries (if available)
    articles_text = []
    if feed_entries:
        for entry in feed_entries[:20]:
            title = getattr(entry, "title", "") or (entry.get("title") if isinstance(entry, dict) else "")
            summary = getattr(entry, "summary", "") or (entry.get("summary") if isinstance(entry, dict) else "")
            articles_text.append(f"{title} {summary}")

    # Fallback to existing sample posts if provided
    if not articles_text and sample_posts:
        for p in sample_posts[:20]:
            articles_text.append(f"{getattr(p, 'title', '')} {getattr(p, 'description', '')}")

    if articles_text:
        total_articles = len(articles_text)
        yemen_count = sum(
            1 for text in articles_text
            if any(kw in text for kw in YEMEN_INDICATORS)
        )
        ratio = yemen_count / total_articles
        # If at least 30% of recent articles cover Yemen or at least 3 articles mention Yemen
        if ratio >= 0.30 or yemen_count >= 3:
            return "موقع يمني"

        # Check if articles have international or pan-Arab focus
        intl_count = sum(
            1 for text in articles_text
            if any(k in text for k in ["البيت الأبيض", "الكرملين", "الأمم المتحدة", "مجلس الأمن", "البنتاغون", "واشنطن", "موسكو"])
        )
        if (intl_count / total_articles) >= 0.40:
            return "موقع دولي"

        return "موقع عربي"

    # 8. Check brief_info or name for general Yemen keywords
    if any(kw in all_text for kw in YEMEN_INDICATORS):
        return "موقع يمني"

    # Default for a Yemeni portal submission with no Arab/international signals
    return "موقع يمني"
