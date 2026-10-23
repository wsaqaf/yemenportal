from django.urls import path
from .views import PostListView, VoteView, PostSearchView, TopicListView
from . import views

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('search/', PostSearchView.as_view(), name='post_search'),
    path('topic/<int:topic_id>/', views.TopicListView.as_view(), name='topic_detail'),
    path('<int:pk>/vote/', VoteView.as_view(), name='vote'),
]
