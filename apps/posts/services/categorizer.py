import re
from django.core.cache import cache
from apps.posts.models import Category, Post


CATEGORY_KEYWORDS = {
    "رياضة": {
        "strong": [
            "كرة القدم", "كرة قدم", "منتخب الناشئين", "منتخب اليمن", "المنتخب الوطني",
            "كأس الخليج", "كأس العالم", "كأس الرابطة", "دوري أبطال", "الدوري الإنجليزي",
            "الدوري الإسباني", "الدوري السعودي", "بطولة", "المباراة", "مباراة", "ركلات الترجيح",
            "نصف نهائي", "ربع نهائي", "الميركاتو", "الكرة الذهبية", "رونالدو", "ميسي",
            "ليفربول", "ريال مدريد", "برشلونة", "مانشستر", "أرسنال", "تشيلسي", "بايرن",
            "أولمبياد", "الأولمبياد", "ألعاب القوى", "السباحة", "التلال", "وحدة عدن",
            "أهلي صنعاء", "شعب إب", "نادي الميناء", "نادي السد", "اتحاد كرة القدم", "فيفا",
        ],
        "medium": [
            "منتخب", "دوري", "ملعب", "مدرب", "لاعب", "لاعبين", "أندية", "نادي ",
            "تأهل", "فوز", "هزيمة", "تعادل", "أهداف", "شباك", "مرمى", "رياضي", "رياضية",
        ],
        "negative": [
            "القوات المسلحة", "عملية عسكرية", "مليشيا", "غارات", "قصف", "صاروخ",
            "ناقلة وقود", "تهديدات الحوثيين", "الصحفيين اليمنيين", "أسعار الصرف",
            "التوقيت الشتوي", "الفوسفاط", "البرلمان",
        ],
    },
    "اقتصاد": {
        "strong": [
            "أسعار الصرف", "سعر الصرف", "أسعار صرف العملات", "الريال اليمني", "البنك المركزي",
            "أسعار الذهب", "سعر الذهب", "الدولار الأمريكي", "الريال السعودي", "التضخم",
            "البنك الدولي", "صندوق النقد", "غرفة التجارة", "الجمارك", "الضرائب",
            "المشتقات النفطية", "أزمة الوقود", "تداول العملات", "شركات الصرافة", "الحوالات المالية",
        ],
        "medium": [
            "اقتصاد", "اقتصادية", "الدولار", "العملات", "الذهب", "النفط", "الغاز",
            "التجارة", "استثمار", "موازنة", "رواتب", "بنك ", "البنوك", "صادرات", "واردات",
        ],
        "negative": ["عملية عسكرية", "مباراة", "منتخب"],
    },
    "صحة": {
        "strong": [
            "منظمة الصحة العالمية", "الصحة العالمية", "وزارة الصحة", "القطاع الصحي",
            "الأوبئة", "الكوليرا", "حمى الضنك", "الملاريا", "شلل الأطفال", "اللقاحات",
            "سوء التغذية", "غسيل الكلى", "مرضى السرطان", "العمليات الجراحية", "المستشفيات",
        ],
        "medium": [
            "صحة", "صحية", "مستشفى", "طبي ", "طبية", "أطباء", "دواء", "أدوية",
            "المرضى", "مرض ", "علاج", "لقاح", "عيادة", "الإسعاف", "اليونيسيف",
        ],
        "negative": ["عملية عسكرية", "مباراة"],
    },
    "تكنولوجيا": {
        "strong": [
            "الذكاء الاصطناعي", "الأمن السيبراني", "ستارلينك", "آيفون", "أندرويد",
            "شركة أبل", "مايكروسوفت", "جوجل", "ميتا", "أوبن إيه آي", "شات جي بي تي",
            "هاتف ذكي", "الهواتف الذكية", "اختراق إلكتروني", "العملات الرقمية", "بيتكوين",
        ],
        "medium": [
            "تكنولوجيا", "تقنية", "تطبيق ", "تطبيقات", "هاتفك", "آبل", "واتساب",
            "برمجيات", "الإنترنت", "الاتصالات", "رقمي", "إلكترونية",
        ],
        "negative": ["عملية عسكرية", "غارات", "قصف"],
    },
    "ثقافة وفن": {
        "strong": [
            "مهرجان ثقافي", "معرض الكتاب", "الفن اليمني", "التراث اليمني", "الشعر اليمني",
            "مسرحية", "فيلم سينمائي", "الفنان ", "الفنانة ", "الأدب العربي", "اتحاد الأدباء",
        ],
        "medium": [
            "ثقافة", "ثقافي", "ثقافية", "فنون", "فن ", "شاعر", "قصيدة", "رواية",
            "تراث", "متحف", "موسيقى", "أغنية", "سينما", "إبداع", "الدسمال",
        ],
        "negative": ["عملية عسكرية", "غارات", "قصف", "مسلحون"],
    },
    "المرأة": {
        "strong": [
            "اللجنة الوطنية للمرأة", "اتحاد نساء اليمن", "تمكين المرأة", "حقوق المرأة",
            "مجلس نساء", "العنف ضد المرأة",
        ],
        "medium": ["المرأة", "النساء", "نسائية", "الفتيات"],
        "negative": [],
    },
    "آراء": {
        "strong": [
            "بقلم:", "بقلم/", "مقال رأي", "وجهة نظر", "زاوية رأي", "كتب:", "يكتب:",
        ],
        "medium": ["مقال ", "مقالات", "قراءة في", "نقد ذاتي"],
        "negative": ["عاجل:", "رويترز", "وكالة سبأ"],
    },
    "تقارير": {
        "strong": [
            "تقرير خاص", "هيومن رايتس ووتش", "مركز أبعاد", "مركز صنعاء للدراسات",
            "تحقيق استقصائي", "تقرير أممي", "تقرير دولي", "حصيلة ضحايا",
        ],
        "medium": ["تقرير:", "تقرير ", "دراسة ", "باحثون", "مركز دراسات", "إحصائية"],
        "negative": [],
    },
    "عاجل": {
        "strong": ["عاجل:", "عاجل |", "عاجل..", "خبر عاجل", "الآن:"],
        "medium": ["عاجل", "انفجار يهز", "غارات جوية", "قصف يستهدف"],
        "negative": [],
    },
}

YEMEN_LOCAL_MARKERS = [
    "اليمن", "يمني", "اليمنية", "صنعاء", "عدن", "تعز", "مأرب", "مارب", "حضرموت",
    "الحديدة", "شبوة", "صعدة", "المكلا", "الضالع", "لحج", "أبين", "المهرة",
    "سقطرى", "البيضاء", "الجوف", "إب ", "ذمار", "عمران", "حجة", "المحويت", "ريمة",
    "الحوثي", "الحوثيين", "الحوثية", "الانتقالي", "الشرعية", "مجلس القيادة",
    "العليمي", "الحكومة اليمنية", "القوات المسلحة", "مطار عدن", "باب المندب",
]

ARAB_MARKERS = [
    "فلسطين", "غزة", "لبنان", "سوريا", "السودان", "مصر", "القاهرة", "العراق",
    "بغداد", "ليبيا", "تونس", "المغرب", "الجزائر", "الأردن", "السعودية", "الرياض",
    "الإمارات", "قطر", "الكويت", "عمان", "البحرين", "جامعة الدول العربية",
]

INTERNATIONAL_MARKERS = [
    "روسيا", "أوكرانيا", "واشنطن", "الولايات المتحدة", "ترامب", "بايدن", "الصين",
    "إيران", "أوروبا", "الاتحاد الأوروبي", "الأمم المتحدة", "مجلس الأمن", "الناتو",
    "إفريقيا", "أكرا", "ألبانيا", "تركيا", "فرنسا", "بريطانيا", "ألمانيا",
]

TAG_SYNONYMS = {
    "رياضة": ["رياضة", "الرياضة", "أخبار الرياضة", "اخبار الرياضة", "كرة قدم", "رياضه", "sports", "sport"],
    "اقتصاد": ["اقتصاد", "إقتصاد", "الاقتصاد", "أخبار الاقتصاد", "مال وأعمال", "أسعار الصرف", "economy", "business"],
    "صحة": ["صحة", "الصحة", "طب وصحة", "صحه", "health"],
    "تكنولوجيا": ["تكنولوجيا", "التكنولوجيا", "علوم وتكنولوجيا", "تقنية", "اتصالات وتقنية", "tech", "technology"],
    "ثقافة وفن": ["ثقافة وفن", "ثقافة", "ثقافة وفنون", "فن وثقافة", "أدب وفن", "فنون", "culture"],
    "المرأة": ["المرأة", "شؤون المرأة", "مرأة", "الاسرة والمرأة"],
    "آراء": ["آراء", "اراء", "مقالات", "مقالات الرأي", "كتاب وآراء", "وجهة نظر", "opinion"],
    "كتاب من اليمن": ["كتاب من اليمن", "أقلام يمنية", "كتاب اليمن"],
    "تقارير": ["تقارير", "تقارير خاصة", "أخبار وتقارير", "تحقيقات", "ملفات وتقارير", "reports"],
    "عاجل": ["عاجل", "أخبار عاجلة"],
    "محلي": ["محلي", "أخبار محلية", "اخبار محلية", "أخبار اليمن", "اخبار اليمن", "الشأن اليمني", "اليمن"],
    "عربي": ["عربي", "أخبار عربية", "الشرق الأوسط", "عربي ودولي"],
    "دولي": ["دولي", "أخبار دولية", "أخبار العالم", "العالم", "دولية"],
}


def get_category_name_to_id_map() -> dict[str, int]:
    """Returns a cached mapping of Category name -> Category ID."""
    cached = cache.get("portal_category_name_map_v1")
    if cached:
        return cached
    mapping = {c.name: c.id for c in Category.objects.all()}
    cache.set("portal_category_name_map_v1", mapping, timeout=3600)
    return mapping


def _is_writer_article_title(title: str) -> bool:
    """Detects columnist/opinion titles like 'مروان الغفوري : حدوده حيث تقف دباباته'."""
    if ":" in title or " - " in title:
        parts = re.split(r"[:\-–]", title, maxsplit=1)
        if len(parts) == 2:
            first_part = parts[0].strip()
            words = first_part.split()
            # Writer name is usually 2-4 words and not a news prefix
            non_writer_prefixes = {
                "عاجل", "تقرير", "شاهد", "فيديو", "مصدر", "عدن", "صنعاء", "تعز",
                "مأرب", "شبوة", "حضرموت", "الحديدة", "اليمن", "الحكومة", "وزارة",
                "القوات", "الأمم", "الصحة", "هيومن", "إيران", "الإمارات", "السعودية",
            }
            if 2 <= len(words) <= 4 and words[0] not in non_writer_prefixes:
                if any(w.startswith(("د.", "أ.", "الشيخ", "الكاتب")) for w in words):
                    return True
    return False


def classify_post_categories(
    title: str,
    description: str = "",
    link: str = "",
    source_name: str = "",
    rss_tags: list[str] | None = None,
) -> list[int]:
    """
    Intelligently classifies a news item on the fly using:
    1. Multi-feature weighted keyword & negative-constraint scoring on title + description
    2. URL path & RSS tag signals (verified against content constraints for topical categories)
    3. Geographic scope classification (محلي vs عربي vs دولي)
    Returns a list of 1 to 3 accurate Category IDs.
    """
    cat_map = get_category_name_to_id_map()
    if not cat_map:
        return []

    title = (title or "").strip()
    desc = (description or "").strip()
    combined = f"{title} {desc}"
    link_lower = (link or "").lower()
    source_name = (source_name or "").strip()

    matched_names: set[str] = set()

    # 1. Check English language articles first
    alpha_chars = re.findall(r"[a-zA-Z\u0600-\u06FF]", title)
    latin_chars = re.findall(r"[a-zA-Z]", title)
    if len(alpha_chars) >= 8 and (len(latin_chars) / len(alpha_chars)) > 0.65:
        if "English" in cat_map:
            return [cat_map["English"]]

    # 2. Evaluate RSS tags via synonym dictionary (with content verification for topical tags)
    tag_candidates: set[str] = set()
    if rss_tags:
        for raw_tag in rss_tags:
            t_clean = (raw_tag or "").strip().lower()
            if not t_clean:
                continue
            for canonical_cat, synonyms in TAG_SYNONYMS.items():
                if any(t_clean == s.lower() or s.lower() in t_clean for s in synonyms):
                    tag_candidates.add(canonical_cat)

    #Also check URL path hints
    if any(p in link_lower for p in ["/sport", "/sports"]):
        tag_candidates.add("رياضة")
    if any(p in link_lower for p in ["/econom", "/business"]):
        tag_candidates.add("اقتصاد")
    if any(p in link_lower for p in ["/opinion", "/articles", "/writers"]):
        tag_candidates.add("آراء")
    if any(p in link_lower for p in ["/health", "/medical"]):
        tag_candidates.add("صحة")
    if any(p in link_lower for p in ["/tech", "/science"]):
        tag_candidates.add("تكنولوجيا")

    # 3. Score topical categories from title & description
    for cat_name, rules in CATEGORY_KEYWORDS.items():
        score = 0
        # Check negative blockers first
        if any(neg in title for neg in rules.get("negative", [])):
            score -= 10

        for kw in rules.get("strong", []):
            if kw in title:
                score += 6
            elif kw in desc:
                score += 3

        for kw in rules.get("medium", []):
            if kw in title:
                score += 3
            elif kw in desc:
                score += 1

        if cat_name in tag_candidates:
            score += 3

        if score >= 5 and cat_name in cat_map:
            matched_names.add(cat_name)

    # Special check for writer/opinion articles
    if _is_writer_article_title(title) or "مقالات" in source_name or "آراء" in source_name:
        if not any(c in matched_names for c in ("رياضة", "اقتصاد", "صحة", "تكنولوجيا")):
            if "آراء" in cat_map:
                matched_names.add("آراء")

    # 4. Geographic / Scope Classification (محلي / عربي / دولي)
    has_yemen = any(m in combined for m in YEMEN_LOCAL_MARKERS)
    has_arab = any(m in title for m in ARAB_MARKERS)
    has_intl = any(m in title for m in INTERNATIONAL_MARKERS)

    if has_yemen:
        if "محلي" in cat_map:
            matched_names.add("محلي")
    elif has_arab:
        if "عربي" in cat_map:
            matched_names.add("عربي")
    elif has_intl:
        if "دولي" in cat_map:
            matched_names.add("دولي")

    # 5. Fallback if no category matched yet
    if not matched_names:
        if has_yemen and "أخبار" in cat_map:
            matched_names.add("أخبار")
        elif "عام" in cat_map:
            matched_names.add("عام")

    return [cat_map[name] for name in matched_names if name in cat_map][:3]


def recategorize_posts_batch(limit: int = 4000) -> int:
    """
    Re-categorizes recent posts AND recent posts inside topical categories using the
    intelligent classifier, cleaning up inaccurate fallback category assignments.
    """
    recent_ids = list(
        Post.objects.filter(state=Post.State.APPROVED)
        .order_by("-published_at")
        .values_list("id", flat=True)[:limit]
    )
    topical_cats = Category.objects.filter(
        name__in=["رياضة", "اقتصاد", "صحة", "تكنولوجيا", "ثقافة وفن", "المرأة", "آراء", "تقارير", "عاجل"]
    )
    topical_post_ids = []
    for cat in topical_cats:
        ids = list(
            Post.objects.filter(state=Post.State.APPROVED, categories=cat)
            .order_by("-published_at")
            .values_list("id", flat=True)[:500]
        )
        topical_post_ids.extend(ids)

    all_target_ids = list(set(recent_ids + topical_post_ids))
    posts = list(
        Post.objects.filter(id__in=all_target_ids)
        .select_related("source")
        .only("id", "title", "description", "link", "source__name")
    )

    ThroughModel = Post.categories.through
    ThroughModel.objects.filter(post_id__in=all_target_ids).delete()

    new_links = []
    for post in posts:
        cat_ids = classify_post_categories(
            title=post.title,
            description=post.description or "",
            link=post.link or "",
            source_name=post.source.name if post.source else "",
        )
        for cid in cat_ids:
            new_links.append(ThroughModel(post_id=post.id, category_id=cid))

    if new_links:
        ThroughModel.objects.bulk_create(new_links, batch_size=1500, ignore_conflicts=True)

    return len(posts)
