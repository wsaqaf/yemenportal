import re
import logging
from datetime import timedelta
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.posts.models import Post, Topic

logger = logging.getLogger(__name__)

ARABIC_STOPWORDS = {
    'في', 'من', 'على', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'تم', 'كان', 'كانت',
    'أن', 'إن', 'قد', 'لا', 'ما', 'هو', 'هي', 'التي', 'الذي', 'الذين', 'بعد',
    'قبل', 'حيث', 'كل', 'ذلك', 'بين', 'أو', 'ثم', 'حتى', 'إذا', 'خلال', 'عاجل',
    'شاهد', 'فيديو', 'بالصور', 'صور', 'تفاصيل', 'الآن', 'اليوم', 'جديد', 'بشأن',
    'حول', 'ضد', 'نحو', 'عقب', 'جراء', 'بسبب', 'تحت', 'فوق', 'امام', 'أمام',
    'لدى', 'منذ', 'عند', 'غير', 'دون', 'سوى', 'كشف', 'يكشف', 'تكشف', 'أعلن',
    'يعلن', 'تعلن', 'أكد', 'يؤكد', 'تؤكد', 'قال', 'يقول', 'تقول', 'مصدر', 'بيان',
    'داخل', 'احد', 'أحد', 'احدى', 'إحدى', 'بشكل', 'بصورة',
    # Days of the week (preventing calendar-based false clustering)
    'الاحد', 'الأحد', 'الاثنين', 'الإثنين', 'الثلاثاء', 'الاربعاء', 'الأربعاء',
    'الخميس', 'الجمعه', 'الجمعة', 'السبت',
    # Gregorian and Hijri months
    'يناير', 'فبراير', 'مارس', 'ابريل', 'أبريل', 'مايو', 'يونيو', 'يوليو',
    'اغسطس', 'أغسطس', 'سبتمبر', 'اكتوبر', 'أكتوبر', 'نوفمبر', 'ديسمبر',
    'محرم', 'صفر', 'ربيع', 'جمادى', 'رجب', 'شعبان', 'رمضان', 'شوال',
    # Routine calendar template terms
    'امس', 'أمس', 'غدا', 'غداً', 'تاريخ', 'الموافق', 'موافق', 'صباح', 'مساء',
    'ليلا', 'ليلة', 'ليله',
}

# Distinctive proper nouns, institutions, and specific event anchors.
# Generic city/governorate names (صنعاء، عدن، تعز) and factions (حوثي، انتقالي) are EXCLUDED
# because they occur in almost every Yemeni headline and cause unrelated events to bleed together.
DISTINCTIVE_ENTITIES = [
    'الأمم المتحدة', 'مجلس الأمن', 'مفوضية حقوق الإنسان', 'العفو الدولية',
    'هيومن رايتس', 'الصحة العالمية', 'اليونيسيف', 'البنك المركزي',
    'مجلس القيادة', 'جامعة تعز', 'مطار عدن', 'مطار صنعاء', 'مطار سيئون',
    'ميناء الحديدة', 'ميناء عدن', 'سفينة صافر', 'ناقلة صافر',
    'كأس الخليج', 'منتخب الناشئين', 'موظف أممي',
    'خالد بحاح', 'رشاد العليمي', 'طارق صالح', 'عيدروس الزبيدي',
    'أحمد بن مبارك', 'معين عبدالملك', 'فولكر تورك', 'هانس غروندبرغ',
    'محمد الشامي', 'إبراهيم الشامي',
]


def _light_stem_word(word: str) -> str:
    """Applies light Arabic prefix and suffix stemming to unify morphological variants."""
    if len(word) <= 3:
        return word

    # Strip common prefixes (وال, بال, فال, كال, لل, ال, و, ب, ف, ل)
    for prefix in ('وال', 'بال', 'فال', 'كال', 'لل'):
        if word.startswith(prefix) and len(word) - len(prefix) >= 3:
            word = word[len(prefix):]
            break
    else:
        if word.startswith('ال') and len(word) >= 5:
            word = word[2:]
        elif word[0] in ('و', 'ب', 'ف', 'ل') and len(word) >= 5:
            if word[1:3] == 'ال' and len(word) >= 6:
                word = word[3:]
            elif word.startswith('ل') and len(word) >= 5:
                word = word[1:]

    # Strip common plural/feminine/possessive suffixes (ون, ين, ات, ان, ية, يه, هم, ها, كم)
    for suffix in ('يون', 'يين', 'يات', 'ون', 'ين', 'ات', 'ان', 'يه', 'هم', 'ها'):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[:-len(suffix)]
            break

    if word.endswith('ه') and len(word) >= 5:
        word = word[:-1]

    # Common irregular plurals and synonyms in Yemeni news
    synonyms = {
        'صواريخ': 'صاروخ',
        'غارات': 'غاره',
        'مليشيات': 'مليشيا',
        'مليشيا': 'حوثي',
        'حوثيين': 'حوثي',
        'حوثيون': 'حوثي',
        'حوث': 'حوثي',
        'انتهاكات': 'انتهاك',
        'عمليات': 'عمليه',
        'قوات': 'قوه',
        'اسعار': 'سعر',
        'عملات': 'عمله',
        'امميه': 'اممي',
        'اممية': 'اممي',
        'معتقلات': 'معتقل',
        'سجون': 'سجن',
        'شهداء': 'شهيد',
        'قتلى': 'قتيل',
        'جرحى': 'جريح',
    }
    return synonyms.get(word, word)


def normalize_arabic(text: str) -> str:
    """Standardizes and lightly stems Arabic text to maximize clustering recall across outlets."""
    if not text:
        return ""
    # Remove tashkeel/diacritics and tatweel
    text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة\b', 'ه', text)
    text = re.sub(r'ى\b', 'ي', text)
    text = re.sub(r'ؤ', 'و', text)
    text = re.sub(r'ئ', 'ي', text)
    # Fix spaced "حو ثي" obfuscation used on social media/portals
    text = re.sub(r'حو\s+ثي', 'حوثي', text)
    text = re.sub(r'[^\w\s]', ' ', text)

    tokens = []
    for raw_w in text.split():
        if raw_w in ARABIC_STOPWORDS or len(raw_w) < 2:
            continue
        # Exclude calendar years (2020..2030, 1440..1450) and day numbers (1..31) from vector text
        if raw_w.isdigit():
            n = int(raw_w)
            if (1 <= n <= 31) or (2020 <= n <= 2030) or (1440 <= n <= 1450):
                continue
        stemmed = _light_stem_word(raw_w)
        if stemmed and stemmed not in ARABIC_STOPWORDS and len(stemmed) >= 2:
            tokens.append(stemmed)
    return " ".join(tokens)


# Pre-normalize distinctive entities using the same pipeline for exact substring matching
DISTINCTIVE_ENTITIES_NORM = [normalize_arabic(e) for e in DISTINCTIVE_ENTITIES if normalize_arabic(e)]


def extract_entities(norm_text: str) -> set[str]:
    """Extracts distinctive institutions, proper nouns, and unique event numbers."""
    found = set()
    for ent in DISTINCTIVE_ENTITIES_NORM:
        if ent in norm_text:
            found.add(ent)
    # Extract distinctive event numbers (e.g. military unit "982", resolution "2216", case numbers)
    # Ignore calendar days (1..31), calendar years (2020..2030, 1440..1450), and generic numbers (10, 24, 100)
    for num in re.findall(r'\b\d{2,5}\b', norm_text):
        n = int(num)
        if (1 <= n <= 31) or (2020 <= n <= 2030) or (1440 <= n <= 1450) or num in ('100', '10', '24'):
            continue
        found.add(f"num_{num}")
    return found


class PostClusterer:
    RELATED_THRESHOLD = 0.28       # Tuned to capture real coverage while eliminating loose semantic bleed
    TOPIC_COHERENCE_MIN = 0.16     # Minimum similarity required with topic's main_post to prevent drift
    LOOKBACK_HOURS = 4             # Optimized 4-hour window to keep topics fresh and active

    def clusterize_recent_posts(self, unclustered_hours: int = 4, force_recluster: bool = False):
        now = timezone.now()
        since = now - timedelta(hours=self.LOOKBACK_HOURS)

        if force_recluster:
            recent_ids = list(
                Post.objects.filter(published_at__gte=since)
                .values_list('id', flat=True)
            )
            Post.objects.filter(id__in=recent_ids).update(topic=None)
            Topic.objects.filter(posts__isnull=True).delete()

        # 1. Fetch unassigned posts from recent window
        unclustered = list(
            Post.objects.filter(
                topic__isnull=True,
                published_at__gte=now - timedelta(hours=unclustered_hours),
                state=Post.State.APPROVED,
            )
            .only('id', 'title', 'description', 'source_id', 'published_at')
            .order_by('published_at')
        )

        if not unclustered:
            logger.info("No unclustered posts to process.")
            return 0

        # 2. Pre-fetch candidates from the lookback window
        candidates = list(
            Post.objects.filter(
                published_at__gte=since,
                state=Post.State.APPROVED,
            )
            .only('id', 'title', 'description', 'source_id', 'topic_id', 'published_at')
            .order_by('published_at')
        )

        if len(candidates) < 2:
            return 0

        candidate_map = {c.id: c for c in candidates}
        candidate_ids = [c.id for c in candidates]
        candidate_texts = [normalize_arabic(c.title) for c in candidates]
        candidate_entities = [extract_entities(t) for t in candidate_texts]

        vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )

        try:
            candidate_tfidf = vectorizer.fit_transform(candidate_texts)
        except ValueError:
            return 0

        existing_topic_ids = {c.topic_id for c in candidates if c.topic_id}
        topic_main_map = {
            t.id: t.main_post
            for t in Topic.objects.filter(id__in=existing_topic_ids).select_related('main_post')
            if t.main_post
        }

        clustered_count = 0
        affected_topic_ids = set()

        for post in unclustered:
            try:
                # Re-check in case post was already assigned a topic earlier in this loop
                in_mem = candidate_map.get(post.id)
                if in_mem and in_mem.topic_id:
                    continue

                norm_title = normalize_arabic(post.title)
                if not norm_title:
                    continue
                post_ents = extract_entities(norm_title)
                post_vec = vectorizer.transform([norm_title])
                sims = cosine_similarity(post_vec, candidate_tfidf).flatten()

                for idx, cid in enumerate(candidate_ids):
                    cand = candidate_map[cid]
                    # Do not match post to itself or same source
                    if cand.id == post.id or cand.source_id == post.source_id:
                        sims[idx] = 0.0
                        continue
                    # Boost similarity if both headlines share specific distinctive entities or numbers
                    if post_ents and candidate_entities[idx]:
                        shared = post_ents.intersection(candidate_entities[idx])
                        if shared:
                            sims[idx] += min(0.14, len(shared) * 0.08)

                # Sort candidate indices by descending similarity
                sorted_indices = (-sims).argsort()
                matched_cand = None

                for s_idx in sorted_indices:
                    score = float(sims[s_idx])
                    if score < self.RELATED_THRESHOLD:
                        break  # No more candidates meet the similarity threshold

                    cand = candidate_map[candidate_ids[s_idx]]

                    # If candidate already belongs to a topic, verify coherence with that topic's main post
                    if cand.topic_id:
                        topic_main = topic_main_map.get(cand.topic_id)
                        if topic_main and topic_main.id != post.id:
                            norm_main = normalize_arabic(topic_main.title)
                            main_vec = vectorizer.transform([norm_main])
                            coherence_sim = float(cosine_similarity(post_vec, main_vec)[0, 0])
                            main_ents = extract_entities(norm_main)
                            if post_ents and main_ents:
                                shared_m = post_ents.intersection(main_ents)
                                if shared_m:
                                    coherence_sim += min(0.14, len(shared_m) * 0.08)
                            if coherence_sim < self.TOPIC_COHERENCE_MIN:
                                # Semantic drift / chaining detected; reject this candidate and check next
                                continue

                    matched_cand = cand
                    break

                if matched_cand:
                    topic_id = matched_cand.topic_id

                    if topic_id:
                        post.topic_id = topic_id
                        post.save(update_fields=['topic_id'])
                        if post.id in candidate_map:
                            candidate_map[post.id].topic_id = topic_id
                        affected_topic_ids.add(topic_id)
                    else:
                        new_topic, _ = Topic.objects.get_or_create(
                            main_post=matched_cand,
                            defaults={'topic_size': 2},
                        )
                        matched_cand.topic_id = new_topic.id
                        matched_cand.save(update_fields=['topic_id'])
                        post.topic_id = new_topic.id
                        post.save(update_fields=['topic_id'])
                        if post.id in candidate_map:
                            candidate_map[post.id].topic_id = new_topic.id
                        topic_main_map[new_topic.id] = matched_cand
                        affected_topic_ids.add(new_topic.id)

                    clustered_count += 1
            except Exception as e:
                logger.error(f"Error clustering post {post.id}: {e}")

        # Recalculate exact topic_size for all touched topics
        for tid in affected_topic_ids:
            cnt = Post.objects.filter(topic_id=tid, state=Post.State.APPROVED).count()
            Topic.objects.filter(id=tid).update(topic_size=cnt)

        # Merge fragmented sub-topics from the lookback window that cover the exact same event
        self._merge_similar_topics(since)

        return clustered_count

    def _merge_similar_topics(self, since):
        topics = list(
            Topic.objects.filter(
                topic_size__gt=1,
                main_post__published_at__gte=since,
            )
            .select_related('main_post')
            .order_by('-topic_size', '-id')[:120]
        )
        if len(topics) < 2:
            return

        texts = [normalize_arabic(t.main_post.title if t.main_post else '') for t in topics]
        ents = [extract_entities(txt) for txt in texts]
        try:
            vec = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2), min_df=1, sublinear_tf=True)
            mat = vec.fit_transform(texts)
            sim_matrix = cosine_similarity(mat)
        except Exception:
            return

        merged_into = {}
        for i in range(len(topics)):
            if topics[i].id in merged_into:
                continue
            for j in range(i + 1, len(topics)):
                if topics[j].id in merged_into:
                    continue
                sim = float(sim_matrix[i, j])
                if ents[i] and ents[j]:
                    shared = ents[i].intersection(ents[j])
                    if shared:
                        sim += min(0.14, len(shared) * 0.08)
                if sim >= 0.40:
                    target_tid = topics[i].id
                    source_tid = topics[j].id
                    Post.objects.filter(topic_id=source_tid).update(topic_id=target_tid)
                    merged_into[source_tid] = target_tid
                    new_cnt = Post.objects.filter(topic_id=target_tid, state=Post.State.APPROVED).count()
                    Topic.objects.filter(id=target_tid).update(topic_size=new_cnt)
                    Topic.objects.filter(id=source_tid).update(topic_size=0)

