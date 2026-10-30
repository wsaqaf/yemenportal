from django.contrib import admin

# Register your models here.


from .models import NewsletterAnnouncement, NewsletterOptOut, CurrencyRate, Post
from django.core.management import call_command
from django.utils.html import format_html

@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ('region', 'currency_code', 'buy_price', 'sell_price', 'updated_at')
    list_filter = ('region', 'currency_code')
    list_editable = ('buy_price', 'sell_price')


@admin.register(NewsletterAnnouncement)
class NewsletterAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject', 'target_group', 'status', 'recipients_count', 'sent_at', 'created_at')
    list_filter = ('status', 'target_group', 'created_at')
    search_fields = ('subject', 'body', 'custom_recipients')
    readonly_fields = ('recipients_count', 'sent_at')
    actions = ['send_to_target_action', 'send_test_action']

    fieldsets = (
        ('تفاصيل الإعلان', {
            'fields': ('subject', 'body', 'is_html')
        }),
        ('تحديد الفئة المستهدفة', {
            'fields': ('target_group', 'custom_recipients', 'test_email'),
            'description': 'اختر من يستلم هذه الرسالة: جميع الأعضاء، المتفاعلون فقط، الإدارة فقط، أو قائمة عناوين مخصصة.'
        }),
        ('حالة الإرسال', {
            'fields': ('status', 'recipients_count', 'sent_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.action(description='🚀 إرسال الإعلان للفئة المستهدفة المحددة')
    def send_to_target_action(self, request, queryset):
        for item in queryset:
            if item.target_group == 'custom' and not item.custom_recipients and not item.test_email:
                self.message_user(request, f'الإعلان #{item.id}: اخترت "قائمة مخصصة" لكن الحقل فارغ! يرجى إدخال عناوين البريد.', level='ERROR')
                continue
            call_command('send_announcement', id=item.id, confirm=True)
            item.refresh_from_db()
            self.message_user(request, f'تم إرسال الإعلان #{item.id} بنجاح إلى {item.recipients_count} مستلم.')

    @admin.action(description='🧪 إرسال تجريبي سريع إلى بريد الاختبار (Test Email)')
    def send_test_action(self, request, queryset):
        for item in queryset:
            if not item.test_email:
                self.message_user(request, f'الإعلان #{item.id}: لا يوجد بريد اختبار محدد في حقل (بريد للاختبار السريع).', level='WARNING')
                continue
            call_command('send_announcement', id=item.id, is_test=True, confirm=True)
            self.message_user(request, f'تم إرسال تجربة الإعلان بنجاح إلى: {item.test_email}')

@admin.register(NewsletterOptOut)
class NewsletterOptOutAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_short', 'source', 'published_at', 'post_views_count', 'impressions_count', 'ctr_display', 'state')
    list_filter = ('state', 'source', 'published_at')
    search_fields = ('title', 'description')
    readonly_fields = ('post_views_count', 'impressions_count', 'ctr_display', 'created_at', 'updated_at')
    list_per_page = 30

    @admin.display(description='عنوان الخبر')
    def title_short(self, obj):
        return (obj.title[:65] + '...') if len(obj.title) > 65 else obj.title

    @admin.display(description='نسبة التفاعل (CTR%)')
    def ctr_display(self, obj):
        val = obj.ctr
        if val >= 5.0:
            color = 'green'
        elif val >= 1.5:
            color = '#2563eb'
        else:
            color = '#6b7280'
        return format_html('<span style="font-weight: bold; color: {};">{}%</span>', color, val)
