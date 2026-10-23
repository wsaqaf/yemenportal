import logging
from django.utils import timezone
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.posts.models import Post, Topic

logger = logging.getLogger(__name__)

class PostClusterer:
    RELATED_THRESHOLD = 0.4
    DUPLICATE_THRESHOLD = 0.95
    LOOKBACK_HOURS = 24

    def clusterize_recent_posts(self):
        """
        Batch-clusters unassigned recent posts against active candidate posts.
        """
        now = timezone.now()
        since = now - timedelta(hours=self.LOOKBACK_HOURS)

        # 1. Fetch unclustered posts from the last 3 hours
        unclustered = list(
            Post.objects.filter(
                topic__isnull=True,
                created_at__gte=now - timedelta(hours=3)
            )
            .only('id', 'title', 'source_id', 'created_at')
            .order_by('created_at')
        )

        if not unclustered:
            logger.info("No unclustered posts found.")
            return

        # 2. Pre-fetch candidates from the last 24h once (avoiding description TOAST)
        candidates = list(
            Post.objects.filter(created_at__gte=since)
            .only('id', 'title', 'source_id', 'topic_id', 'created_at')
        )

        if not candidates:
            return

        candidate_map = {c.id: c for c in candidates}
        candidate_ids = [c.id for c in candidates]
        candidate_texts = [c.title for c in candidates]

        # 3. Vectorize all candidate titles in a single matrix
        vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
        try:
            candidate_tfidf = vectorizer.fit_transform(candidate_texts)
        except ValueError:
            return

        for post in unclustered:
            try:
                post_vec = vectorizer.transform([post.title])
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
                        Topic.objects.filter(id=topic.id).update(topic_size=topic.posts.count())
                    else:
                        new_topic = Topic.objects.create(main_post=matched_post, topic_size=2)
                        matched_post.topic = new_topic
                        matched_post.save(update_fields=['topic'])
                        post.topic = new_topic
                        post.save(update_fields=['topic'])
                elif max_score < self.RELATED_THRESHOLD:
                    # Isolated story: create new topic seed
                    new_topic = Topic.objects.create(main_post=post, topic_size=1)
                    post.topic = new_topic
                    post.save(update_fields=['topic'])
            except Exception as e:
                logger.error(f"Error clustering post {post.id}: {e}")
