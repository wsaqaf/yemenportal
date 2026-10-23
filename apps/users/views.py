from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import User

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

# Users Management List View
class UserManageListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'users/manage_list.html'
    context_object_name = 'users_list'
    paginate_by = 15

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(email__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


# Toggle User Active/Blocked Status
def toggle_user_status(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('index')
        
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "لا يمكنك حظر حسابك الشخصي!")
    else:
        user.is_active = not user.is_active
        user.save()
        status_str = "تفعيل" if user.is_active else "حظر"
        messages.success(request, f"تم {status_str} حساب '{user.email}' بنجاح.")
        
    return redirect('users:manage_list')


# Delete User Permanently
def delete_user(request, pk):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('index')
        
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "لا يمكنك حذف حسابك الشخصي!")
    else:
        email = user.email
        user.delete()
        messages.warning(request, f"تم حذف حساب المستخدم '{email}' وكل بياناته نهائياً.")
        
    return redirect('users:manage_list')
