from django.db import models


class PublishedChannelPost(models.Model):
    class Channel(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        FACEBOOK = 'facebook', 'Facebook'
        TWITTER = 'twitter', 'Twitter'

    class PostType(models.TextChoices):
        HOT_CLUSTER = 'hot_cluster', 'تغطية مجمعة (عنقود)'
        BREAKING = 'breaking', 'خبر عاجل'
        EXCHANGE_RATES = 'exchange_rates', 'أسعار الصرف'
        DIGEST = 'digest', 'موجز إخباري'

    class Status(models.TextChoices):
        PUBLISHED = 'published', 'تم النشر'
        FAILED = 'failed', 'فشل النشر'

    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.TELEGRAM)
    post_type = models.CharField(max_length=30, choices=PostType.choices)
    topic = models.ForeignKey(
        'posts.Topic',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='channel_publications',
        verbose_name='العنقود الخبري'
    )
    post = models.ForeignKey(
        'posts.Post',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='channel_publications',
        verbose_name='الخبر الرئيسي'
    )
    external_message_id = models.CharField(max_length=100, blank=True, verbose_name='معرف الرسالة في المنصة')
    message_text = models.TextField(verbose_name='نص المنشور')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    error_message = models.TextField(blank=True, verbose_name='رسالة الخطأ إن وجدت')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='تاريخ ووقت النشر')

    class Meta:
        verbose_name = 'منشور قناة التواصل'
        verbose_name_plural = 'منشورات قنوات التواصل'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_channel_display()}] {self.get_post_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
