
"""
URL configuration for NAKL project.

Django Version: 6.1.2
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


# --------------------------------------------------
# NAKL Admin Configuration
# --------------------------------------------------

admin.site.site_header = 'إدارة منصة نقل للتخليص الجمركي'
admin.site.site_title = 'NAKL | لوحة التحكم'
admin.site.index_title = 'لوحة إدارة منصة التخليص الجمركي'


# --------------------------------------------------
# URL Patterns
# --------------------------------------------------

urlpatterns = [

    # Homepage - home.html
    path(
        '',
        TemplateView.as_view(template_name='home.html'),
        name='home'
    ),

    # Django Admin Dashboard
    path('OMAR/', admin.site.urls),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Catalog - Customs Services
    path('catalog/', include('catalog.urls')),

    # Orders
    path('orders/', include('orders.urls')),

]


# --------------------------------------------------
# Media Files - Development Only
# --------------------------------------------------

if settings.DEBUG and not settings.CLOUDINARY_ENABLED:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
