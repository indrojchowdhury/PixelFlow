from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import dashboard_key
from .services import build_dashboard


class DashboardView(APIView):
    def get(self, request):
        key = dashboard_key(request.user.id)
        data = cache.get(key)
        hit = data is not None

        if not hit:
            data = build_dashboard(request.user)
            cache.set(key, data, settings.DASHBOARD_CACHE_SECONDS)

        response = Response(data)
        response["X-Cache"] = "HIT" if hit else "MISS"
        return response