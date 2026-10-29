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
    'قبل', 'حيث', 'كل', 'ذلك', 'بين', 'أو', 'ثم', 'حتى', 'إذا', 'خلال'
}

def normalize_arabic(text: str) -> str:
    """Standardizes Arabic characters to increase clustering recall."""
    if not text:
        return ""
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة\b', 'ه', text)
    text = re.sub(r'ى\b', 'ي', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

class PostClusterer:
    RELATED_THRESHOLD = 0.28       # Lowered from 0.40 to capture varying coverage styles
    DUPLICATE_THRESHOLD = 0.95
    LOOKBACK_HOURS = 36            # Time window for matching related news

    def clusterize_recent_posts(self):
        now = timezone.now()
        since = now - timedelta(hours=self.LOOKBACK_HOURS)

        # 1. Fetch unassigned posts from the last 6 hours
        unclustered = list(
            Post.objects.filter(
                topic__isnull=True,
                created_at__gte=now - timedelta(hours=6)
            )
            .only('id', 'title', 'source_id', 'created_at')
            .order_by('created_at')
        )

        if not unclustered:
            logger.info("No unclustered posts to process.")
            return

        # 2. Pre-fetch candidates from the lookback window
        candidates = list(
            Post.objects.filter(created_at__gte=since)
            .only('id', 'title', 'source_id', 'topic_id', 'created_at')
        )

        if len(candidates) < 2:
            return

        candidate_map = {c.id: c for c in candidates}
        candidate_ids = [c.id for c in candidates]
        candidate_texts = [normalize_arabic(c.title) for c in candidates]

        vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b',
            stop_words=list(ARABIC_STOPWORDS),
            ngram_range=(1, 2),
            min_df=1
        )
        
        try:
            candidate_tfidf = vectorizer.fit_transform(candidate_texts)
        except ValueError:
            return

        for post in unclustered:
            try:
                norm_title = normalize_arabic(post.title)
                post_vec = vectorizer.transform([norm_title])
                sims = cosine_similarity(post_vec, candidate_tfidf).flatten()

                # Zero out comparisons against the post itself or the same source
                for idx, cid in enumerate(candidate_ids):
                    cand = candidate_map[cid]
                    if cand.id == post.id or cand.source_id == post.source_id:
                        sims[idx] = 0.0

                max_idx = sims.argmax()
                max_score = sims[max_idx]

                if self.RELATED_THRESHOLD <= max_score < self.DUPLICATE_THRESHOLD:
                    matched_post = candidate_map[candidate_ids[max_idx]]
                    topic = matched_post.topic or getattr(matched_post, 'main_topic_of', None)

                    if topic:
                        post.topic = topic
                        post.save(update_fields=['topic'])
                        actual_count = Post.objects.filter(topic=topic).count()
                        Topic.objects.filter(id=topic.id).update(topic_size=actual_count)
                    else:
                        new_topic = Topic.objects.create(main_post=matched_post, topic_size=2)
                        matched_post.topic = new_topic
                        matched_post.save(update_fields=['topic'])
                        post.topic = new_topic
                        post.save(update_fields=['topic'])
                # If score < RELATED_THRESHOLD, leave post.topic as None (isolated post)
            except Exception as e:
                logger.error(f"Error clustering post {post.id}: {e}")
