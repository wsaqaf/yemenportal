from django.urls import path
from .views import UserManageListView, toggle_user_status, delete_user

app_name = 'users'

urlpatterns = [
    path('manage/', UserManageListView.as_view(), name='manage_list'),
    path('manage/<int:pk>/toggle/', toggle_user_status, name='toggle_user_status'),
    path('manage/<int:pk>/delete/', delete_user, name='delete_user'),
]
