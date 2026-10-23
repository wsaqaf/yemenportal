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
            queryset = queryset.filter(models.Q(title__icontains=q) | models.Q(description__icontains=q))

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
