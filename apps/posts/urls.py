from .newsletter import NewsletterUnsubscribeView
from django.urls import path
from django.views.generic import RedirectView
from .views import PostListView, VoteView, PostSearchView, TopicListView, PostDetailView, MostReadListView, ArchiveListView, CurrencyServiceView
from . import views

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('most-read/', MostReadListView.as_view(), name='most_read'),
    path('archive/', ArchiveListView.as_view(), name='archive'),
    path('currency/', CurrencyServiceView.as_view(), name='currency_service'),
    path('search/', PostSearchView.as_view(), name='post_search'),
    path('record-impressions/', views.RecordImpressionsView.as_view(), name='record_impressions'),
    path('check-top-story/', views.CheckTopStoryView.as_view(), name='check_top_story'),
    path('topic/<int:topic_id>/', views.TopicListView.as_view(), name='topic_detail'),
    
    # Core Post Detail Route (Matches /posts/<pk>/)
    path('newsletter/unsubscribe/<str:token>/', NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    
    # 301 Permanent Redirects for legacy Rails sub-routes
    path('<int:pk>/header', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/header/', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/reviews', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/reviews/', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    
    path('<int:pk>/vote/', VoteView.as_view(), name='vote'),
]
