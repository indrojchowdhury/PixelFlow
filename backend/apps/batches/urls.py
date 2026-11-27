from rest_framework.routers import SimpleRouter

from .views import BatchViewSet

router = SimpleRouter()
router.register("", BatchViewSet, basename="batch")

urlpatterns = router.urls