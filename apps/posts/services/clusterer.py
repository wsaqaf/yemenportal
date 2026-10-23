import logging
from django.utils import timezone
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from apps.posts.models import Post, Topic

logger = logging.getLogger(__name__)

class PostClusterer:
    # Thresholds based on Rails app config (assumed)
    RELATED_THRESHOLD = 0.4
    DUPLICATE_THRESHOLD = 0.95
    LOOKBACK_HOURS = 24

    def clusterize_recent_posts(self):
        """
        Main entry point to clusterize recent pending posts.
        """
        unclustered_posts = Post.objects.filter(
            topic__isnull=True,
            created_at__gte=timezone.now() - timedelta(hours=3)
        ).order_by('created_at')

        for post in unclustered_posts:
            self.attach_topic(post)

    def attach_topic(self, post):
        """
        Finds a topic for a post or creates a new one.
        """
        related_topic = self.find_related_topic(post)
        
        if related_topic:
            post.topic = related_topic
            post.save()
            # Update topic size counter
            related_topic.topic_size = related_topic.posts.count()
            related_topic.save()
            logger.info(f"Attached post {post.id} to existing topic {related_topic.id}")
        else:
            # Create new topic with this post as main
            new_topic = Topic.objects.create(main_post=post, topic_size=1)
            post.topic = new_topic
            post.save()
            logger.info(f"Created new topic {new_topic.id} for post {post.id}")

    def find_related_topic(self, post):
        """
        Uses TF-IDF and Cosine Similarity to find a related topic.
        """
        # Load candidate posts for comparison (excluding the current post and posts from same source)
        candidates = Post.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=self.LOOKBACK_HOURS)
        ).exclude(id=post.id).exclude(source=post.source)

        if not candidates.exists():
            return None

        # Prepare text data
        texts = [post.title + " " + (post.description or "")]
        for c in candidates:
            texts.append(c.title + " " + (c.description or ""))

        # Vectorize
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError: # Empty vocabulary
            return None

        # Calculate similarity between the new post (index 0) and all others
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # Find the best match
        max_sim_idx = similarities.argmax()
        max_sim_val = similarities[max_sim_idx]

        if max_sim_val >= self.RELATED_THRESHOLD and max_sim_val < self.DUPLICATE_THRESHOLD:
            best_match_post = candidates[int(max_sim_idx)]
            # Best match's topic (or the match itself as a main post)
            return best_match_post.topic or getattr(best_match_post, 'main_topic_of', None)
        
        return None
