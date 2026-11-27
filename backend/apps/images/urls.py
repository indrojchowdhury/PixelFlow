from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ImageUploadView, ImageViewSet

router = SimpleRouter()
router.register("", ImageViewSet, basename="image")

# "upload/" must come before the router, otherwise it matches the detail route
urlpatterns = [
    path("upload/", ImageUploadView.as_view(), name="image-upload"),
] + router.urls