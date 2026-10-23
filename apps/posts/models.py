from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.sources.models import Source

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class Topic(models.Model):
    main_post = models.OneToOneField(
        'Post', 
        on_delete=models.CASCADE, 
        related_name='main_topic_of',
        null=True,
        blank=True
    )
    topic_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Topic for {self.main_post_id}"

class Post(models.Model):
    class State(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    link = models.TextField(unique=True)
    published_at = models.DateTimeField()
    
    state = models.CharField(max_length=20, choices=State.choices, default=State.APPROVED)
    image_url = models.TextField(blank=True, null=True)
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    
    # Topic clustering
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='posts'
    )
    
    # Metrics
    voting_result = models.IntegerField(default=0)
    post_views_count = models.IntegerField(default=0)
    review_rating = models.IntegerField(default=0)
    
    # For search/NLP
    stemmed_text = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def upvoted_by_user(self):
        # This is a bit inefficient for lists, but fine for now
        # Better to annotate in the queryset
        return getattr(self, '_upvoted_by_user', False)

    @property
    def downvoted_by_user(self):
        return getattr(self, '_downvoted_by_user', False)

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField() # 1 for upvote, -1 for downvote
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='post_views'
    )
    ip_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
