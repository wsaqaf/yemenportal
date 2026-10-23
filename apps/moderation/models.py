from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.posts.models import Post

class Flag(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, null=True)
    resolve = models.BooleanField(default=False)
    rate = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='moderated_reviews'
    )
    flag = models.ForeignKey(Flag, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.post.title} by {self.moderator.email}"

class ReviewComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='review_comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='author_review_comments'
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"
