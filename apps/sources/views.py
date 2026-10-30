from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db import models
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import feedparser
import requests

from .models import Source, SourceLog
from .forms import SourceForm, SourceSuggestionForm
from apps.posts.models import Post

# Public Source List View
class SourceListView(ListView):
    model = Source
    template_name = 'sources/source_list.html'
    context_object_name = 'sources'
    paginate_by = 12

    def get_queryset(self):
        return Source.objects.filter(approve_state=Source.ApproveState.APPROVED).order_by('name')


from django.contrib.auth.views import redirect_to_login

# Staff-only Mixin
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "يرجى تسجيل الدخول بحساب المشرف للوصول إلى هذه الصفحة.")
            return redirect_to_login(self.request.get_full_path())
        
        messages.error(self.request, "عذراً، هذا الحساب لا يملك صلاحيات الإشراف المطلوبة للوصول إلى الصفحة.")
        return redirect('/')

# Manage Sources List View with Advanced Filtering & Metrics
class SourceManageListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Source
    template_name = 'sources/manage_list.html'
    context_object_name = 'sources'
    paginate_by = 15  # Set pagination to 15 as requested

    def get_queryset(self):
        queryset = Source.objects.all().annotate(
            total_posts=models.Count('posts')
        ).order_by('-created_at')

        # Advanced Filters
        state_filter = self.request.GET.get('state')
        approve_filter = self.request.GET.get('approve_state')

        if state_filter:
            queryset = queryset.filter(state=state_filter)
        if approve_filter:
            queryset = queryset.filter(approve_state=approve_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Fetch latest crawler log for each source
        latest_logs = {}
        log_ids = SourceLog.objects.values('source_id').annotate(max_id=models.Max('id')).values('max_id')
        for log in SourceLog.objects.filter(id__in=log_ids):
            latest_logs[log.source_id] = log
        context['latest_logs'] = latest_logs

        # 2. Calculate advanced metrics per source in the queryset
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(days=7)
        one_month_ago = now - timedelta(days=30)

        source_metrics = {}
        for source in context['sources']:
            # Post frequencies
            daily_count = source.posts.filter(created_at__gte=one_day_ago).count()
            weekly_count = source.posts.filter(created_at__gte=one_week_ago).count()

            # Average Votes per article (weekly & monthly)
            weekly_votes = source.posts.filter(published_at__gte=one_week_ago).aggregate(avg_val=models.Avg('voting_result'))['avg_val'] or 0.0
            monthly_votes = source.posts.filter(published_at__gte=one_month_ago).aggregate(avg_val=models.Avg('voting_result'))['avg_val'] or 0.0

            source_metrics[source.id] = {
                'daily_frequency': daily_count,
                'weekly_frequency': weekly_count,
                'weekly_avg_votes': round(weekly_votes, 1),
                'monthly_avg_votes': round(monthly_votes, 1),
            }

        context['source_metrics'] = source_metrics
        context['current_state'] = self.request.GET.get('state', '')
        context['current_approve_state'] = self.request.GET.get('approve_state', '')
        return context


# Add Source (Admin only)
class SourceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Source
    form_class = SourceForm
    template_name = 'sources/manage_form.html'
    success_url = reverse_lazy('sources:manage_list')

    def form_valid(self, form):
        messages.success(self.request, f"تمت إضافة المصدر '{form.cleaned_data['name']}' بنجاح.")
        return super().form_valid(form)


# Edit Source (Admin only)
class SourceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Source
    form_class = SourceForm
    template_name = 'sources/manage_form.html'
    success_url = reverse_lazy('sources:manage_list')

    def form_valid(self, form):
        messages.success(self.request, f"تم تعديل المصدر '{form.cleaned_data['name']}' بنجاح.")
        return super().form_valid(form)


# Delete Source (Admin only)
class SourceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Source
    template_name = 'sources/manage_confirm_delete.html'
    success_url = reverse_lazy('sources:manage_list')

    def delete(self, request, *args, **kwargs):
        source = self.get_object()
        messages.warning(request, f"تم حذف المصدر '{source.name}' بنجاح.")
        return super().delete(request, *args, **kwargs)


# Member Suggest Source View with RSS Verification
class SourceSuggestView(LoginRequiredMixin, CreateView):
    model = Source
    form_class = SourceSuggestionForm
    template_name = 'sources/suggest_form.html'
    success_url = reverse_lazy('sources:source_list')

    def form_valid(self, form):
        # 1. Verify RSS feed works well with robust fallback
        feed_url = form.cleaned_data['link']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        feed_valid = True
        verification_error = None
        
        try:
            # Try normal secure request first
            res = requests.get(feed_url, headers=headers, timeout=12, verify=True)
            res.raise_for_status()
            feed = feedparser.parse(res.content)
            
            # Check if feed contains invalid structure
            if getattr(feed, 'bozo', 0) == 1 and not feed.entries:
                raise Exception("Format not recognized as a valid RSS feed")
        except Exception as e1:
            # Retry with verify=False in case of SSL chain issues
            try:
                res = requests.get(feed_url, headers=headers, timeout=12, verify=False)
                res.raise_for_status()
                feed = feedparser.parse(res.content)
                if getattr(feed, 'bozo', 0) == 1 and not feed.entries:
                    raise Exception("Format not recognized as a valid RSS feed")
            except Exception as e2:
                # Flag feed as invalid but DO NOT block the user from submitting
                feed_valid = False
                verification_error = str(e2)

        # 2. Dynamic AI-driven classification (Yemeni / Arab / International)
        from apps.sources.classifier import classify_source_scope
        feed_entries = getattr(feed, 'entries', []) if feed_valid and 'feed' in locals() else None
        source_scope = classify_source_scope(
            name=form.cleaned_data.get('name', ''),
            website_url=form.cleaned_data.get('website', ''),
            feed_url=feed_url,
            brief_info=form.cleaned_data.get('brief_info', ''),
            feed_entries=feed_entries,
        )

        # 3. Save suggestion with state based on verification results
        source = form.save(commit=False)
        source.user = self.request.user
        source.source_type = source_scope
        source.approve_state = Source.ApproveState.SUGGESTED
        source.state = Source.State.VALID if feed_valid else Source.State.INVALID
        source.save()

        # 3. Send emails
        # A. Notify Yemen Portal Admin
        moderation_url = self.request.build_absolute_uri(
            reverse('sources:manage_moderate', args=[source.id])
        )
        admin_subject = f"اقتراح مصدر جديد: {source.name}"
        admin_context = {
            'source': source,
            'user': self.request.user,
            'moderation_url': moderation_url,
            'feed_valid': feed_valid,
            'verification_error': verification_error,
        }
        admin_html = render_to_string('sources/emails/suggest_notify_admin.html', admin_context)
        admin_plain = strip_tags(admin_html)
        send_mail(
            admin_subject,
            admin_plain,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@yemenportal.net'],
            html_message=admin_html,
            fail_silently=True
        )

        # 4. Message to user
        if feed_valid:
            messages.success(
                self.request, 
                "تم إرسال تفاصيل المصدر الإخباري المقترح إلى إدارة يمن بورتال للنظر فيه. سيتم اتخاذ القرار وإرسال بريد إلكتروني بالقرار إلى حسابك قريباً."
            )
        else:
            messages.success(
                self.request,
                "تم تسجيل اقتراح المصدر بنجاح! ملاحظة: واجه خادم الموقع صعوبة مؤقتة في التحقق التلقائي من رابط الـ RSS (قد يكون ذلك بسبب جدار الحماية أو قيود خادم الاستضافة)، ولكن سيقوم مسؤولو الموقع بمراجعة الرابط وتفعيله يدوياً قريباً."
            )
        return redirect('sources:source_list')


# Admin Moderation View for Suggested Source
class SourceModerateView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Source
    template_name = 'sources/manage_moderate.html'
    context_object_name = 'source'

    def post(self, request, *args, **kwargs):
        source = self.get_object()
        action = request.POST.get('action')

        if action == 'approve':
            source.approve_state = Source.ApproveState.APPROVED
            source.save()
            messages.success(request, f"تمت الموافقة وتفعيل المصدر '{source.name}' بنجاح.")
            
            # Send approval email to suggesting user
            if source.user and source.user.email:
                subject = f"تم قبول المصدر الإخباري المقترح: {source.name}"
                html_msg = render_to_string('sources/emails/suggest_approved_user.html', {'source': source})
                plain_msg = strip_tags(html_msg)
                send_mail(
                    subject,
                    plain_msg,
                    settings.DEFAULT_FROM_EMAIL,
                    [source.user.email],
                    html_message=html_msg,
                    fail_silently=True
                )
        elif action == 'reject':
            source.approve_state = Source.ApproveState.REJECTED
            source.save()
            messages.warning(request, f"تم رفض المصدر المقترح '{source.name}'.")

            # Send rejection email to suggesting user
            if source.user and source.user.email:
                subject = f"بخصوص المصدر الإخباري المقترح: {source.name}"
                html_msg = render_to_string('sources/emails/suggest_rejected_user.html', {'source': source})
                plain_msg = strip_tags(html_msg)
                send_mail(
                    subject,
                    plain_msg,
                    settings.DEFAULT_FROM_EMAIL,
                    [source.user.email],
                    html_message=html_msg,
                    fail_silently=True
                )

        return redirect('sources:manage_list')
