import logging
import os

from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.batches.services import create_batch, dispatch_batch
from apps.dashboard.cache import invalidate_dashboard

from .models import Image
from .serializers import ImageSerializer, ImageUploadSerializer
from .validators import ImageValidationError, inspect_image

logger = logging.getLogger(__name__)


class ImageUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ImageUploadSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        album = serializer.validated_data["album"]
        files = serializer.validated_data["files"]

        created = []
        rejected = []
        batch = None

        with transaction.atomic():
            for uploaded_file in files:
                safe_name = os.path.basename(uploaded_file.name)[:255]
                try:
                    info = inspect_image(uploaded_file)
                except ImageValidationError as exc:
                    rejected.append({"name": safe_name, "error": str(exc)})
                    continue

                image = Image(
                    user=request.user,
                    album=album,
                    original_name=safe_name,
                    original_size=info["size"],
                    width=info["width"],
                    height=info["height"],
                    format=info["format"],
                    status=Image.Status.PENDING,
                )
                image.original_file.save(safe_name, uploaded_file, save=False)
                image.save()
                created.append(image)

            if created:
                batch = create_batch(request.user, album, created)
                batch_id = batch.id
                # Dispatch only after commit so workers can always see the rows
                transaction.on_commit(lambda: dispatch_batch(batch_id))

        if created:
            invalidate_dashboard(request.user.id)

        data = {
            "batch_id": batch.id if batch else None,
            "created": ImageSerializer(
                created, many=True, context={"request": request}
            ).data,
            "rejected": rejected,
        }

        if not created:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_202_ACCEPTED)


class ImageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ImageSerializer

    def get_queryset(self):
        # Ownership check: other users' images return 404
        queryset = Image.objects.filter(user=self.request.user).prefetch_related("versions")

        if self.action == "list":
            album_id = self.request.query_params.get("album")
            status_value = self.request.query_params.get("status")
            if album_id and album_id.isdigit():
                queryset = queryset.filter(album_id=album_id)
            if status_value in Image.Status.values:
                queryset = queryset.filter(status=status_value)

        return queryset

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_dashboard(self.request.user.id)