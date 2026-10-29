from django.contrib import admin

# Register your models here.


from .models import NewsletterAnnouncement, NewsletterOptOut
from django.core.management import call_command

@admin.register(NewsletterAnnouncement)
class NewsletterAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'recipients_count', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'body')
    readonly_fields = ('recipients_count', 'sent_at')
    actions = ['send_announcement_action']

    @admin.action(description='إرسال الإعلان المختار لجميع الأعضاء المشتركين')
    def send_announcement_action(self, request, queryset):
        for item in queryset:
            call_command('send_announcement', id=item.id)
        self.message_user(request, 'تم إرسال الإعلان/الإعلانات المختارة بنجاح.')

@admin.register(NewsletterOptOut)
class NewsletterOptOutAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
