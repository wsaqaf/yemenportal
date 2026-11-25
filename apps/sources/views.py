from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db import models
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
import threading
import feedparser
import requests

from .models import Source, SourceLog
from .forms import SourceForm, SourceSuggestionForm
from apps.posts.models import Post

logger = logging.getLogger(__name__)

SOURCE_STATS_CACHE_PREFIX = 'sources:manage_stats:v1:'
SOURCE_STATS_CACHE_TTL = 300  # 5 minutes


def _send_mail_async(subject, plain_message, recipient_list, html_message=None):
    """Send notification email without blocking the HTTP moderation response."""
    def _worker():
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send source notification email")

    if getattr(settings, 'EMAIL_BACKEND', '').endswith(('locmem.EmailBackend', 'dummy.EmailBackend')):
        _worker()
    else:
        threading.Thread(target=_worker, daemon=True).start()


def _invalidate_source_caches(source_id=None):
    cache.delete('global_approved_sources_list')
    if source_id is not None:
        cache.delete(f'{SOURCE_STATS_CACHE_PREFIX}{source_id}')

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
        # Keep queryset lean so pagination count and slicing never scan the 4.5M+ posts table.
        queryset = Source.objects.all().order_by('-created_at')

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
        page_sources = list(context['sources'])
        page_ids = [source.id for source in page_sources]

        latest_logs = {}
        source_metrics = {}

        if page_ids:
            # 1. Fetch latest crawler log ONLY for the sources on the current page
            max_log_ids = list(
                SourceLog.objects.filter(source_id__in=page_ids)
                .values('source_id')
                .annotate(max_id=models.Max('id'))
                .values_list('max_id', flat=True)
            )
            if max_log_ids:
                for log in SourceLog.objects.filter(id__in=max_log_ids):
                    latest_logs[log.source_id] = log

            # 2. Fetch per-source post counts & metrics from Redis cache, computing only misses
            #    in two indexed aggregate queries scoped strictly to the current page.
            cache_keys = {sid: f'{SOURCE_STATS_CACHE_PREFIX}{sid}' for sid in page_ids}
            cached_stats = cache.get_many(cache_keys.values())
            missing_ids = [sid for sid, key in cache_keys.items() if key not in cached_stats]

            if missing_ids:
                now = timezone.now()
                one_day_ago = now - timedelta(days=1)
                one_week_ago = now - timedelta(days=7)
                one_month_ago = now - timedelta(days=30)

                # Hits partial index idx_posts_approved_source_pub (source_id, published_at DESC)
                totals_map = dict(
                    Post.objects.filter(
                        source_id__in=missing_ids,
                        state=Post.State.APPROVED,
                    )
                    .values('source_id')
                    .annotate(total=models.Count('id'))
                    .values_list('source_id', 'total')
                )

                recent_rows = (
                    Post.objects.filter(
                        source_id__in=missing_ids,
                        state=Post.State.APPROVED,
                        published_at__gte=one_month_ago,
                    )
                    .values('source_id')
                    .annotate(
                        daily_frequency=models.Count('id', filter=models.Q(published_at__gte=one_day_ago)),
                        weekly_frequency=models.Count('id', filter=models.Q(published_at__gte=one_week_ago)),
                        weekly_avg_votes=models.Avg('voting_result', filter=models.Q(published_at__gte=one_week_ago)),
                        monthly_avg_votes=models.Avg('voting_result'),
                    )
                )
                recent_map = {row['source_id']: row for row in recent_rows}

                to_cache = {}
                for sid in missing_ids:
                    row = recent_map.get(sid, {})
                    entry = {
                        'total_posts': totals_map.get(sid, 0),
                        'daily_frequency': row.get('daily_frequency') or 0,
                        'weekly_frequency': row.get('weekly_frequency') or 0,
                        'weekly_avg_votes': round(row.get('weekly_avg_votes') or 0.0, 1),
                        'monthly_avg_votes': round(row.get('monthly_avg_votes') or 0.0, 1),
                    }
                    to_cache[cache_keys[sid]] = entry
                    cached_stats[cache_keys[sid]] = entry

                cache.set_many(to_cache, timeout=SOURCE_STATS_CACHE_TTL)

            for source in page_sources:
                entry = cached_stats.get(cache_keys[source.id], {})
                source.total_posts = entry.get('total_posts', 0)
                source_metrics[source.id] = {
                    'daily_frequency': entry.get('daily_frequency', 0),
                    'weekly_frequency': entry.get('weekly_frequency', 0),
                    'weekly_avg_votes': entry.get('weekly_avg_votes', 0.0),
                    'monthly_avg_votes': entry.get('monthly_avg_votes', 0.0),
                }

        context['sources'] = page_sources
        context['latest_logs'] = latest_logs
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
        response = super().form_valid(form)
        _invalidate_source_caches(self.object.id)
        messages.success(self.request, f"تمت إضافة المصدر '{form.cleaned_data['name']}' بنجاح.")
        return response


# Edit Source (Admin only)
class SourceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Source
    form_class = SourceForm
    template_name = 'sources/manage_form.html'
    success_url = reverse_lazy('sources:manage_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        _invalidate_source_caches(self.object.id)
        messages.success(self.request, f"تم تعديل المصدر '{form.cleaned_data['name']}' بنجاح.")
        return response


# Delete Source (Admin only)
class SourceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Source
    template_name = 'sources/manage_confirm_delete.html'
    success_url = reverse_lazy('sources:manage_list')

    def form_valid(self, form):
        source = self.get_object()
        source_id = source.id
        source_name = source.name
        response = super().form_valid(form)
        _invalidate_source_caches(source_id)
        messages.warning(self.request, f"تم حذف المصدر '{source_name}' بنجاح.")
        return response


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
        previous_state = source.approve_state

        if action == 'approve':
            source.approve_state = Source.ApproveState.APPROVED
            source.state = Source.State.VALID
            source.save(update_fields=['approve_state', 'state', 'updated_at'])
            _invalidate_source_caches(source.id)

            if previous_state == Source.ApproveState.APPROVED:
                messages.info(request, f"المصدر '{source.name}' مقبول ومفعل مسبقاً.")
            else:
                messages.success(request, f"تمت الموافقة وتفعيل المصدر '{source.name}' بنجاح.")
                # Send approval email to suggesting user asynchronously
                if source.user and source.user.email:
                    subject = f"تم قبول المصدر الإخباري المقترح: {source.name}"
                    html_msg = render_to_string('sources/emails/suggest_approved_user.html', {'source': source})
                    plain_msg = strip_tags(html_msg)
                    _send_mail_async(subject, plain_msg, [source.user.email], html_message=html_msg)
        elif action == 'reject':
            source.approve_state = Source.ApproveState.REJECTED
            source.save(update_fields=['approve_state', 'updated_at'])
            _invalidate_source_caches(source.id)

            if previous_state == Source.ApproveState.REJECTED:
                messages.info(request, f"المصدر '{source.name}' مرفوض مسبقاً.")
            else:
                messages.warning(request, f"تم رفض المصدر المقترح '{source.name}'.")
                # Send rejection email to suggesting user asynchronously
                if source.user and source.user.email:
                    subject = f"بخصوص المصدر الإخباري المقترح: {source.name}"
                    html_msg = render_to_string('sources/emails/suggest_rejected_user.html', {'source': source})
                    plain_msg = strip_tags(html_msg)
                    _send_mail_async(subject, plain_msg, [source.user.email], html_message=html_msg)

        return redirect('sources:manage_list')
