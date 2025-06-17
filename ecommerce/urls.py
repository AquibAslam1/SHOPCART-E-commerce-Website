"""ecommerce URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your ecommerce app
    path('', include("ecommerceapp.urls")),   # Includes index, contact, about, checkout, profile, search

    # Your authentication system
    path('auth/', include("authcart.urls")),  # Includes login, register, logout, etc.
]

# Serve media files in development (images, product photos)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
