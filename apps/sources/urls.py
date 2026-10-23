from django.urls import path
from .views import (
    SourceListView,
    SourceSuggestView,
    SourceManageListView,
    SourceCreateView,
    SourceUpdateView,
    SourceDeleteView,
    SourceModerateView
)

app_name = 'sources'

urlpatterns = [
    # Public URLs
    path('', SourceListView.as_view(), name='source_list'),
    path('suggest/', SourceSuggestView.as_view(), name='source_suggest'),
    
    # Management URLs (Staff only)
    path('manage/', SourceManageListView.as_view(), name='manage_list'),
    path('manage/add/', SourceCreateView.as_view(), name='manage_add'),
    path('manage/<int:pk>/edit/', SourceUpdateView.as_view(), name='manage_edit'),
    path('manage/<int:pk>/delete/', SourceDeleteView.as_view(), name='manage_delete'),
    path('manage/<int:pk>/moderate/', SourceModerateView.as_view(), name='manage_moderate'),
]
