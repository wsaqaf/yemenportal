from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.ModerationDashboardView.as_view(), name='dashboard'),
    path('approve/<int:pk>/', views.approve_post, name='approve_post'),
    path('reject/<int:pk>/', views.reject_post, name='reject_post'),
]
