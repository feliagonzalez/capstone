# capstone/urls.py

from django.contrib import admin
from django.urls import path, include
# --- AÑADE ESTAS DOS LÍNEAS ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# --- AÑADE ESTO AL FINAL ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)