from django.contrib import admin
from django.utils.html import format_html
from .models import Flag, Review, ReviewComment, PostReport

@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'rate', 'resolve')
    list_editable = ('rate', 'resolve')

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'flag', 'reporter', 'ip_address', 'is_resolved', 'created_at')
    list_filter = ('flag', 'is_resolved', 'created_at')
    search_fields = ('post__title', 'custom_reason', 'ip_address', 'reporter__email')
    raw_id_fields = ('post', 'reporter')
    readonly_fields = ('created_at', 'post_direct_link', 'article_preview')
    list_editable = ('is_resolved',)
    actions = ['mark_resolved', 'reject_reported_posts']

    def post_title(self, obj):
        return obj.post.title[:60] if obj.post else '-'
    post_title.short_description = 'عنوان الخبر'

    def post_direct_link(self, obj):
        if obj.post:
            url = f"/posts/{obj.post.id}/"
            unflag_url = f"/moderation/unflag/{obj.post.id}/"
            reject_url = f"/moderation/reject/{obj.post.id}/"
            return format_html(
                '<a href="{}" target="_blank" style="font-weight:bold;color:#2563eb;margin-left:12px;">🔗 فتح الخبر</a> '
                '<a href="{}" style="font-weight:bold;color:#16a34a;background:#dcfce7;padding:4px 10px;border-radius:6px;text-decoration:none;margin-left:8px;">✅ إلغاء البلاغ (إبقاء الخبر)</a> '
                '<a href="{}" style="font-weight:bold;color:#dc2626;background:#fee2e2;padding:4px 10px;border-radius:6px;text-decoration:none;">⛔ حجب الخبر</a>',
                url, unflag_url, reject_url
            )
        return '-'
    post_direct_link.short_description = 'إجراءات سريعة'

    def article_preview(self, obj):
        if obj.post:
            return format_html(
                '<div style="max-width:650px;background:#f8fafc;padding:12px;border-radius:8px;border:1px solid #e2e8f0;line-height:1.7;">'
                '<strong>العنوان:</strong> {}<br>'
                '<strong>المصدر:</strong> {}<br>'
                '<strong>الحالة الحالية:</strong> {}<br>'
                '<strong>الرابط الخارجي:</strong> <a href="{}" target="_blank">رابط المصدر الأصلي</a>'
                '</div>',
                obj.post.title,
                obj.post.source.name if obj.post.source else 'غير محدد',
                obj.post.get_state_display() if hasattr(obj.post, 'get_state_display') else obj.post.state,
                obj.post.link or '#'
            )
        return '-'
    article_preview.short_description = 'بيانات وتفاصيل الخبر'

    @admin.action(description='إلغاء البلاغات المحددة (تجاهل البلاغ)')
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

    @admin.action(description='حجب الأخبار المُبلغ عنها فوراً')
    def reject_reported_posts(self, request, queryset):
        for report in queryset:
            if report.post:
                report.post.state = 'rejected'
                report.post.save()
        queryset.update(is_resolved=True)
