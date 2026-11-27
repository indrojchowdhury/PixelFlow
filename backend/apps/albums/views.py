from django.db.models import Count
from rest_framework import viewsets

from .models import Album
from .serializers import AlbumSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer

    def get_queryset(self):
        # Ownership check: users only ever see their own albums.
        # image_count is annotated in one query, so there is no N+1 problem.
        # Django drops Meta.ordering for GROUP BY queries, so order explicitly.
        return (
            Album.objects.filter(user=self.request.user)
            .annotate(image_count=Count("images"))
            .order_by("-created_at", "-id")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)