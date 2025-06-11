"""
URL configuration for petshop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.content.urls')),
    path('shop/', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('api/', include('apps.core.urls_api')),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
