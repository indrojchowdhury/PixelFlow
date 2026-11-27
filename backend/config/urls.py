from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/albums/", include("apps.albums.urls")),
    path("api/images/", include("apps.images.urls")),
    path("api/batches/", include("apps.batches.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
]

# Serve uploaded media in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)