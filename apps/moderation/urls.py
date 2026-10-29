from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.ModerationDashboardView.as_view(), name='dashboard'),
    path('approve/<int:pk>/', views.approve_post, name='approve_post'),
    path('reject/<int:pk>/', views.reject_post, name='reject_post'),
    path('unflag/<int:pk>/', views.unflag_post, name='unflag_post'),
    path('report/<int:pk>/', views.submit_post_report, name='submit_report'),
]
