from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.db import connection
from email.utils import parseaddr
from apps.posts.models import Post
from apps.sources.models import Source
from .models import PostReport, Flag
from django.contrib.auth.views import redirect_to_login

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "يرجى تسجيل الدخول بحساب المشرف للوصول إلى هذه الصفحة.")
            return redirect_to_login(self.request.get_full_path())
        messages.error(self.request, "عذراً، هذا الحساب لا يملك صلاحيات الإشراف المطلوبة.")
        return redirect('/')

class FastModerationPaginator(Paginator):
    """
    Prevents running slow SELECT COUNT(*) across 4.4+ million records
    when paginating approved posts.
    """
    @cached_property
    def count(self):
        from django.core.cache import cache
        if hasattr(self.object_list, 'query') and 'approved' in str(self.object_list.query):
            cached_val = cache.get('moderation_approved_count')
            if cached_val:
                return cached_val
        return super().count

class ModerationDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Post
    template_name = 'moderation/dashboard.html'
    context_object_name = 'posts'
    paginate_by = 15
    paginator_class = FastModerationPaginator

    def get_queryset(self):
        state = self.request.GET.get('state', 'reported')
        source = self.request.GET.get('source')

        if state == 'reported':
            # Fast index lookup using idx_postreport_unresolved
            unresolved_post_ids = PostReport.objects.filter(is_resolved=False).values_list('post_id', flat=True)
            queryset = Post.objects.filter(id__in=unresolved_post_ids).select_related('source').prefetch_related('reports', 'reports__flag')
        elif state:
            queryset = Post.objects.filter(state=state).select_related('source')
        else:
            queryset = Post.objects.all().select_related('source')

        if source:
            queryset = queryset.filter(source_id=source)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.core.cache import cache

        context['reported_count'] = PostReport.objects.filter(is_resolved=False).values('post_id').distinct().count()
        context['pending_count'] = Post.objects.filter(state='pending').count()

        approved_count = cache.get('moderation_approved_count')
        if approved_count is None:
            try:
                # Fast metadata estimate (0.001s) instead of scanning 4.4M rows
                with connection.cursor() as cursor:
                    cursor.execute("SELECT reltuples::bigint FROM pg_class WHERE relname = 'posts_post';")
                    row = cursor.fetchone()
                    approx_total = row[0] if row and row[0] > 0 else 4440000
                approved_count = approx_total
            except Exception:
                approved_count = Post.objects.filter(state='approved').count()
            cache.set('moderation_approved_count', approved_count, timeout=1800)
        context['approved_count'] = approved_count

        rejected_count = cache.get('moderation_rejected_count')
        if rejected_count is None:
            rejected_count = Post.objects.filter(state='rejected').count()
            cache.set('moderation_rejected_count', rejected_count, timeout=600)
        context['rejected_count'] = rejected_count

        context['sources'] = Source.objects.all().order_by('name')
        context['current_source'] = self.request.GET.get('source')
        context['current_state'] = self.request.GET.get('state', 'reported')
        return context

def approve_post(request, pk):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect('index')
    post = get_object_or_404(Post, pk=pk)
    post.state = 'approved'
    post.save()
    PostReport.objects.filter(post=post).update(is_resolved=True)
    if request.headers.get('HX-Request'):
        return render(request, 'moderation/partials/post_row_empty.html', {'post': post})
    messages.success(request, f"تمت الموافقة على الخبر '{post.title}'.")
    return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

def reject_post(request, pk):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect('index')
    post = get_object_or_404(Post, pk=pk)
    post.state = 'rejected'
    post.save()
    PostReport.objects.filter(post=post).update(is_resolved=True)
    if request.headers.get('HX-Request'):
        return render(request, 'moderation/partials/post_row_empty.html', {'post': post})
    messages.warning(request, f"تم حجب الخبر '{post.title}'.")
    return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

def unflag_post(request, pk):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect('index')
    post = get_object_or_404(Post, pk=pk)
    PostReport.objects.filter(post=post).update(is_resolved=True)
    if request.headers.get('HX-Request'):
        return render(request, 'moderation/partials/post_row_empty.html', {'post': post})
    messages.success(request, f"تم إلغاء البلاغ والإبقاء على الخبر '{post.title}'.")
    return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

@require_POST
def submit_post_report(request, pk):
    post = get_object_or_404(Post, pk=pk)
    flag_id = request.POST.get('flag_id')
    custom_reason = (request.POST.get('custom_reason') or '').strip()

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

    flag = None
    if flag_id:
        flag = Flag.objects.filter(id=flag_id).first()

    report = PostReport.objects.create(
        post=post,
        reporter=request.user if request.user.is_authenticated else None,
        flag=flag,
        custom_reason=custom_reason,
        ip_address=ip
    )

    try:
        recipient_list = [addr for _, addr in getattr(settings, 'ADMINS', []) if addr]
        if not recipient_list:
            _, fallback = parseaddr(getattr(settings, 'DEFAULT_FROM_EMAIL', ''))
            recipient_list = [fallback] if fallback else ['admin@yemenportal.net']

        flag_name = flag.name if flag else 'غير ذلك'
        reporter_label = request.user.email if request.user.is_authenticated else f"زائر ({ip})"
        admin_url = f"http://194.163.154.154/admin/moderation/postreport/{report.id}/change/"
        post_url = f"http://194.163.154.154/posts/{post.id}/"
        reject_url = f"http://194.163.154.154/moderation/reject/{post.id}/"
        unflag_url = f"http://194.163.154.154/moderation/unflag/{post.id}/"
        mod_dash_url = "http://194.163.154.154/moderation/?state=reported"
        source_name = post.source.name if post.source else 'غير محدد'
        details_text = custom_reason if custom_reason else 'لم تُكتب تفاصيل إضافية'

        subject = f"[يمن بورتال] بلاغ محتوى جديد: {flag_name}"
        plain_msg = (
            f"تم استلام بلاغ جديد عن محتوى مخالف في يمن بورتال:\n\n"
            f"• عنوان الخبر: {post.title}\n"
            f"• المصدر: {source_name}\n"
            f"• نوع المخالفة: {flag_name}\n"
            f"• تفاصيل الشكوى: {details_text}\n"
            f"• المبلّغ: {reporter_label}\n\n"
            f"خيارات المعالجة السريعة:\n"
            f"1. رابط الخبر على الموقع: {post_url}\n"
            f"2. إلغاء البلاغ (إبقاء الخبر): {unflag_url}\n"
            f"3. حجب الخبر فوراً: {reject_url}\n"
            f"4. لوحة الإشراف: {mod_dash_url}\n"
        )

        html_msg = (
            '<!DOCTYPE html>'
            '<html dir="rtl" lang="ar">'
            '<head><meta charset="utf-8"></head>'
            '<body dir="rtl" style="font-family: Tahoma, Arial, sans-serif; background-color: #f8fafc; padding: 20px; text-align: right;">'
            '<div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;">'
            '<div style="background: #0284c7; color: #ffffff; padding: 16px; text-align: center;">'
            '<h2 style="margin: 0; font-size: 18px;">يمن بورتال - بلاغ عن محتوى</h2>'
            '</div>'
            '<div style="padding: 20px;">'
            f'<p><span style="background: #fee2e2; color: #dc2626; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 13px;">نوع المخالفة: {flag_name}</span></p>'
            f'<p><b>عنوان الخبر:</b> {post.title}</p>'
            f'<p><b>المصدر:</b> {source_name}</p>'
            f'<p><b>تفاصيل الشكوى:</b> {details_text}</p>'
            f'<p><b>المبلّغ:</b> {reporter_label}</p>'
            '<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #f1f5f9; text-align: center;">'
            f'<a href="{post_url}" target="_blank" style="display: inline-block; padding: 8px 14px; margin: 4px; border-radius: 6px; text-decoration: none; font-weight: bold; background: #0284c7; color: #ffffff;">🔗 فتح الخبر</a> '
            f'<a href="{unflag_url}" target="_blank" style="display: inline-block; padding: 8px 14px; margin: 4px; border-radius: 6px; text-decoration: none; font-weight: bold; background: #16a34a; color: #ffffff;">✅ إلغاء البلاغ</a> '
            f'<a href="{reject_url}" target="_blank" style="display: inline-block; padding: 8px 14px; margin: 4px; border-radius: 6px; text-decoration: none; font-weight: bold; background: #dc2626; color: #ffffff;">⛔ حجب الخبر</a><br>'
            f'<a href="{mod_dash_url}" target="_blank" style="display: inline-block; padding: 6px 12px; margin-top: 10px; border-radius: 6px; text-decoration: none; font-size: 13px; background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;">الانتقال إلى لوحة الإشراف</a>'
            '</div></div></div></body></html>'
        )

        send_mail(
            subject=subject,
            message=plain_msg,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@yemenportal.net'),
            recipient_list=recipient_list,
            html_message=html_msg,
            fail_silently=True
        )
    except Exception:
        pass

    return JsonResponse({
        'status': 'success',
        'message': 'شكراً لك، تم استلام بلاغك وسيقوم فريق المراجعة بالتحقق منه فوراً.'
    })
