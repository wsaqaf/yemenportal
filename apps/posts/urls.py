from django.urls import path
from django.views.generic import RedirectView
from .views import PostListView, VoteView, PostSearchView, TopicListView, PostDetailView
from . import views

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('search/', PostSearchView.as_view(), name='post_search'),
    path('topic/<int:topic_id>/', views.TopicListView.as_view(), name='topic_detail'),
    
    # Core Post Detail Route (Matches /posts/<pk>/)
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    
    # 301 Permanent Redirects for legacy Rails sub-routes
    path('<int:pk>/header', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/header/', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/reviews', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    path('<int:pk>/reviews/', RedirectView.as_view(pattern_name='posts:post_detail', permanent=True)),
    
    path('<int:pk>/vote/', VoteView.as_view(), name='vote'),
]
