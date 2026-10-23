from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from apps.posts.models import Post
from apps.sources.models import Source

from django.contrib.auth.views import redirect_to_login

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.info(self.request, "يرجى تسجيل الدخول بحساب المشرف للوصول إلى هذه الصفحة.")
            return redirect_to_login(self.request.get_full_path())
        
        messages.error(self.request, "عذراً، هذا الحساب لا يملك صلاحيات الإشراف المطلوبة للوصول إلى الصفحة.")
        return redirect('/')
class ModerationDashboardView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Post
    template_name = 'moderation/dashboard.html'
    context_object_name = 'posts'
    paginate_by = 15

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-created_at')
        state = self.request.GET.get('state', 'pending')
        source = self.request.GET.get('source')
        
        if state:
            queryset = queryset.filter(state=state)
        if source:
            queryset = queryset.filter(source_id=source)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = Post.objects.filter(state='pending').count()
        context['approved_count'] = Post.objects.filter(state='approved').count()
        context['rejected_count'] = Post.objects.filter(state='rejected').count()
        context['sources'] = Source.objects.all().order_by('name')
        context['current_state'] = self.request.GET.get('state', 'pending')
        context['current_source'] = self.request.GET.get('source')
        return context

def approve_post(request, pk):
    if not request.user.is_staff:
        return redirect('index')
    post = get_object_or_404(Post, pk=pk)
    post.state = 'approved'
    post.save()
    if request.headers.get('HX-Request'):
        return render(request, 'moderation/partials/post_row_empty.html', {'post': post})
    messages.success(request, f"Article '{post.title}' approved.")
    return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))

def reject_post(request, pk):
    if not request.user.is_staff:
        return redirect('index')
    post = get_object_or_404(Post, pk=pk)
    post.state = 'rejected'
    post.save()
    if request.headers.get('HX-Request'):
        return render(request, 'moderation/partials/post_row_empty.html', {'post': post})
    messages.warning(request, f"Article '{post.title}' rejected.")
    return redirect(request.META.get('HTTP_REFERER', 'moderation:dashboard'))
