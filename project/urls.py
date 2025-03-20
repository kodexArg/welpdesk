from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='logout_page'), name='logout'),
    path('logout_page/', TemplateView.as_view(template_name='registration/logout.html'), name='logout_page'),
]

# Django Browser Reload (DEBUG)
urlpatterns += [
    path("__reload__/", include("django_browser_reload.urls")),
]


# Add URL patterns for serving static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('development/', TemplateView.as_view(template_name='development.html'), name='development'),
    ]
