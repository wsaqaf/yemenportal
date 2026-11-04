from django.contrib import admin
from .models import PublishedChannelPost


@admin.register(PublishedChannelPost)
class PublishedChannelPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'post_type', 'topic_link', 'status', 'created_at')
    list_filter = ('channel', 'post_type', 'status', 'created_at')
    search_fields = ('message_text', 'external_message_id', 'topic__main_post__title')
    readonly_fields = ('created_at',)

    def topic_link(self, obj):
        if obj.topic and obj.topic.main_post:
            return obj.topic.main_post.title[:50]
        elif obj.post:
            return obj.post.title[:50]
        return "-"
    topic_link.short_description = 'الخبر / الموضوع'
