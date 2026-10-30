from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from apps.posts.views import PostListView, MostReadListView, ArchiveListView, CurrencyServiceView
from apps.posts.pwa_views import pwa_manifest, pwa_service_worker, pwa_offline

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # Progressive Web App (PWA)
    path('manifest.json', pwa_manifest, name='pwa_manifest_json'),
    path('manifest.webmanifest', pwa_manifest, name='pwa_manifest'),
    path('sw.js', pwa_service_worker, name='pwa_service_worker'),
    path('offline/', pwa_offline, name='pwa_offline'),
    
    # Apps & Portal Services
    path('', PostListView.as_view(), name='home'),
    path('most-read/', MostReadListView.as_view(), name='most_read'),
    path('archive/', ArchiveListView.as_view(), name='archive'),
    path('services/currency/', CurrencyServiceView.as_view(), name='currency_service'),
    path('posts/', include('apps.posts.urls', namespace='posts')),
    path('moderation/', include('apps.moderation.urls', namespace='moderation')),
    path('sources/', include('apps.sources.urls')),
    path('users/', include('apps.users.urls', namespace='users')),
    
    # Static Pages
    path('about_us/', TemplateView.as_view(template_name='static/about_us.html'), name='about_us'),
    path('terms_of_use/', TemplateView.as_view(template_name='static/terms_of_use.html'), name='terms_of_use'),
    path('qs_and_as/', TemplateView.as_view(template_name='static/qs_and_as.html'), name='qs_and_as'),
    path('contact_us/', TemplateView.as_view(template_name='static/contact_us.html'), name='contact_us'),
    
    # HTMX
    # path('__debug__/', include('debug_toolbar.urls')), # Handled in DEBUG block below
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
