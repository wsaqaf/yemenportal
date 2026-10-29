from .utils import is_iframe_allowed
import re

def normalize_arabic_search_variants(term: str) -> list[str]:
    term = term.strip()
    if not term:
        return []
    variants = {term}
    
    # 1. Alif / Hamza normalization (أ, إ, آ <-> ا)
    alif_unified = re.sub(r'[أإآ]', 'ا', term)
    variants.add(alif_unified)
    # If term uses plain alif, test common hamza forms
    if 'ا' in term:
        variants.add(term.replace('ا', 'أ', 1))
        variants.add(term.replace('ا', 'إ', 1))
    
    # 2. Taa Marbuta / Haa normalization (ة <-> ه)
    if term.endswith('ة'):
        variants.add(term[:-1] + 'ه')
    elif term.endswith('ه'):
        variants.add(term[:-1] + 'ة')
        
    # 3. Yaa / Alif Maqsura (ي <-> ى)
    if term.endswith('ي'):
        variants.add(term[:-1] + 'ى')
    elif term.endswith('ى'):
        variants.add(term[:-1] + 'ي')

    return [v for v in variants if v][:4]

from apps.posts.paginator import CachedCountPaginator
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponse
from apps.posts.models import Post, Vote

class PostListView(ListView):
    paginator_class = CachedCountPaginator
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    allow_empty = True

    def paginate_queryset(self, queryset, page_size):
        try:
            return super().paginate_queryset(queryset, page_size)
        except Exception:
            # Catch all pagination errors (out of range, not a number, etc.)
            # and force return the first page.
            paginator = self.get_paginator(
                queryset,
                page_size,
                orphans=self.get_paginate_orphans(),
                allow_empty_first_page=True,
            )
            page = paginator.page(1)
            return (paginator, page, page.object_list, page.has_other_pages())

    def get_template_names(self):
        if getattr(self.request, "htmx", False):
            return ['posts/partials/post_list_items.html']
        return [self.template_name]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.filter(state=Post.State.APPROVED).select_related('source', 'topic').prefetch_related('categories')
        
        # 1. Filtering by Query
        q = self.request.GET.get('q')
        if q:
            q_clean = q.strip()
            if q_clean:
                variants = normalize_arabic_search_variants(q_clean)
                q_filter = models.Q()
                for var in variants:
                    q_filter |= models.Q(title__icontains=var)
                queryset = queryset.filter(q_filter)

        # 2. Filtering by Period
        period = self.request.GET.get('period')
        if period:
            from django.utils import timezone
            from datetime import timedelta
            now = timezone.now()
            if period == '1h': queryset = queryset.filter(published_at__gte=now - timedelta(hours=1))
            elif period == '24h': queryset = queryset.filter(published_at__gte=now - timedelta(days=1))
            elif period == 'week': queryset = queryset.filter(published_at__gte=now - timedelta(weeks=1))
            elif period == 'month': queryset = queryset.filter(published_at__gte=now - timedelta(days=30))
            elif period == 'year': queryset = queryset.filter(published_at__gte=now - timedelta(days=365))

        # 3. Filtering by Source/Category
        sources = self.request.GET.getlist('sources')
        if sources: queryset = queryset.filter(source_id__in=sources)
        
        categories = self.request.GET.getlist('categories')
        if categories: queryset = queryset.filter(categories__id__in=categories)

        # 4. Sorting
        sort = self.request.GET.get('sort', 'latest')
        if sort == 'votes': queryset = queryset.order_by('-voting_result', '-published_at')
        elif sort == 'reads': queryset = queryset.order_by('-post_views_count', '-published_at')
        else: queryset = queryset.order_by('-published_at')

        if user.is_authenticated:
            from django.db.models import Exists, OuterRef
            queryset = queryset.annotate(
                is_upvoted=Exists(Vote.objects.filter(user=user, post=OuterRef('pk'), value=1)),
                is_downvoted=Exists(Vote.objects.filter(user=user, post=OuterRef('pk'), value=-1))
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_categories'] = self.request.GET.getlist('categories')
        context['selected_sources'] = self.request.GET.getlist('sources')

        from apps.posts.services.portal_services import (
            get_homepage_portal_widgets,
            get_exchange_rates,
            get_yemen_weather,
        )
        widgets = get_homepage_portal_widgets()
        context.update(widgets)
        context['exchange_rates'] = get_exchange_rates()
        context['yemen_weather'] = get_yemen_weather()

        page_num = self.request.GET.get('page', '1')
        has_filters = any([
            self.request.GET.get('q'),
            self.request.GET.get('period'),
            self.request.GET.get('sort') and self.request.GET.get('sort') != 'latest',
            context['selected_categories'],
            context['selected_sources'],
            self.kwargs.get('topic_id'),
        ])
        context['show_portal_hero'] = (str(page_num) in ('1', '') and not has_filters)
        return context


class MostReadListView(ListView):
    model = Post
    template_name = 'posts/most_read.html'
    context_object_name = 'posts'
    paginate_by = 30

    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        window = self.request.GET.get('window', '24h')
        base_qs = (
            Post.objects.filter(state=Post.State.APPROVED)
            .select_related('source', 'topic')
            .prefetch_related('categories')
        )

        if window == '10h':
            qs = base_qs.filter(published_at__gte=now - timedelta(hours=10))
        elif window == 'week':
            qs = base_qs.filter(published_at__gte=now - timedelta(days=7))
        elif window == 'all':
            qs = base_qs
        else:
            qs = base_qs.filter(published_at__gte=now - timedelta(hours=24))

        qs = qs.order_by('-post_views_count', '-voting_result', '-published_at')
        if qs.count() < 5 and window in ('10h', '24h'):
            qs = base_qs.order_by('-post_views_count', '-voting_result', '-published_at')
        return qs[:30]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_window'] = self.request.GET.get('window', '24h')
        from apps.posts.services.portal_services import (
            get_homepage_portal_widgets,
            get_exchange_rates,
            get_yemen_weather,
        )
        widgets = get_homepage_portal_widgets()
        context['opinion_posts'] = widgets.get('opinion_posts', [])
        context['top_sources'] = widgets.get('top_sources', [])
        context['exchange_rates'] = get_exchange_rates()
        context['yemen_weather'] = get_yemen_weather()
        return context


class ArchiveListView(PostListView):
    template_name = 'posts/archive.html'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        date_str = self.request.GET.get('date', '').strip()
        year = self.request.GET.get('year', '').strip()
        month = self.request.GET.get('month', '').strip()
        day = self.request.GET.get('day', '').strip()

        if date_str:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(published_at__date=parsed_date)
                return queryset
            except ValueError:
                pass

        if year and year.isdigit() and int(year) > 1990:
            queryset = queryset.filter(published_at__year=int(year))
        if month and month.isdigit() and 1 <= int(month) <= 12:
            queryset = queryset.filter(published_at__month=int(month))
        if day and day.isdigit() and 1 <= int(day) <= 31:
            queryset = queryset.filter(published_at__day=int(day))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        current_year = timezone.now().year
        context['archive_years'] = list(range(current_year, 2008, -1))
        context['archive_months'] = [
            (1, 'يناير'), (2, 'فبراير'), (3, 'مارس'), (4, 'أبريل'),
            (5, 'مايو'), (6, 'يونيو'), (7, 'يوليو'), (8, 'أغسطس'),
            (9, 'سبتمبر'), (10, 'أكتوبر'), (11, 'نوفمبر'), (12, 'ديسمبر'),
        ]
        context['archive_days'] = list(range(1, 32))
        context['selected_year'] = self.request.GET.get('year', '')
        context['selected_month'] = self.request.GET.get('month', '')
        context['selected_day'] = self.request.GET.get('day', '')
        context['selected_date'] = self.request.GET.get('date', '')
        return context


class CurrencyServiceView(ListView):
    model = Post
    template_name = 'posts/currency_service.html'
    context_object_name = 'economic_posts'
    paginate_by = 15

    def get_queryset(self):
        return (
            Post.objects.filter(state=Post.State.APPROVED)
            .filter(
                models.Q(categories__name__in=['اقتصاد', 'إقتصاد'])
                | models.Q(title__icontains='صرف')
                | models.Q(title__icontains='الريال')
                | models.Q(title__icontains='الدولار')
                | models.Q(title__icontains='البنك')
            )
            .select_related('source', 'topic')
            .prefetch_related('categories')
            .distinct()
            .order_by('-published_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.posts.services.portal_services import (
            get_exchange_rates,
            get_yemen_weather,
            get_homepage_portal_widgets,
        )
        context['exchange_rates'] = get_exchange_rates()
        context['yemen_weather'] = get_yemen_weather()
        widgets = get_homepage_portal_widgets()
        context['top_sources'] = widgets.get('top_sources', [])
        return context


class PostSearchView(PostListView):
    template_name = 'posts/post_search.html'
    paginate_by = 12

class TopicListView(PostListView):
    template_name = 'posts/post_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        topic_id = self.kwargs.get('topic_id')
        return queryset.filter(topic_id=topic_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.posts.models import Topic
        context['current_topic'] = get_object_or_404(Topic, pk=self.kwargs.get('topic_id'))
        return context

class VoteView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = f'/accounts/login/?next={request.META.get("HTTP_REFERER", "/")}'
            return response

        from django.db import transaction
        from django.db.models import Sum

        post = get_object_or_404(Post, pk=pk)
        try:
            value = int(request.POST.get('value', 0))
            if value not in (1, -1):
                return HttpResponse(status=400)
        except (ValueError, TypeError):
            return HttpResponse(status=400)

        with transaction.atomic():
            vote = Vote.objects.filter(user=request.user, post=post).first()
            if vote:
                if vote.value == value:
                    vote.delete()
                    user_voted = 0
                else:
                    vote.value = value
                    vote.save(update_fields=['value'])
                    user_voted = value
            else:
                Vote.objects.create(user=request.user, post=post, value=value)
                user_voted = value

            total = post.votes.aggregate(total_score=Sum('value'))['total_score'] or 0
            post.voting_result = total
            post.save(update_fields=['voting_result'])

        return render(request, 'posts/partials/vote_buttons.html', {
            'post': post,
            'user_voted': user_voted
        })

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404

class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        post_id = self.kwargs.get(self.pk_url_kwarg or 'pk')
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        is_bot = any(bot in ua for bot in ['bot', 'crawl', 'spider', 'slurp', 'facebookexternalhit'])
        
        # تجنب احتساب البوتات وتجنب تكرار احتساب الزائر عند عمل Refresh
        session_key = f'viewed_post_{post_id}'
        if not is_bot and not request.session.get(session_key, False):
            Post.objects.filter(pk=post_id).update(post_views_count=models.F('post_views_count') + 1)
            try:
                request.session[session_key] = True
            except Exception:
                pass

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Allow viewing approved posts, using select_related to eliminate extra queries
        return Post.objects.select_related('source', 'topic').prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['allows_iframe'] = is_iframe_allowed(post.link or (post.source.website if post.source else ''), post.source)
        # If part of an event cluster/topic, load up to 5 other related articles
        if post.topic_id:
            context['related_posts'] = (
                Post.objects.filter(topic_id=post.topic_id, state=Post.State.APPROVED)
                .exclude(id=post.id)
                .select_related('source')
                .only('id', 'title', 'published_at', 'source__name', 'image_url')
                .order_by('-published_at')[:5]
            )
        else:
            context['related_posts'] = []
        return context
