from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Source(models.Model):
    class State(models.TextChoices):
        VALID = 'valid', _('Valid')
        INVALID = 'invalid', _('Invalid')

    class ApproveState(models.TextChoices):
        SUGGESTED = 'suggested', _('Suggested')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    name = models.CharField(max_length=255)
    link = models.URLField(max_length=1000, unique=True) # Usually the RSS feed link
    website = models.URLField(max_length=1000, blank=True, null=True)
    brief_info = models.TextField(blank=True, null=True)
    
    admin_name = models.CharField(max_length=255, blank=True, null=True)
    admin_email = models.EmailField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    source_type = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.VALID)
    approve_state = models.CharField(max_length=20, choices=ApproveState.choices, default=ApproveState.SUGGESTED)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggested_sources'
    )
    
    iframe_flag = models.BooleanField(default=True)
    logo_url = models.URLField(max_length=1000, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class SourceLog(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='logs')
    state = models.CharField(max_length=50, blank=True, null=True)
    posts_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source.name} log at {self.created_at}"
