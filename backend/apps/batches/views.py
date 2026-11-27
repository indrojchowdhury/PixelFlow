from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ProcessingBatch
from .serializers import BatchSerializer


class BatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BatchSerializer

    def get_queryset(self):
        # Ownership check: other users' batches return 404
        return ProcessingBatch.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        batch = self.get_object()

        if batch.status in (
            ProcessingBatch.Status.PENDING,
            ProcessingBatch.Status.PROCESSING,
        ):
            return Response(
                {"detail": "The batch is still processing."},
                status=status.HTTP_409_CONFLICT,
            )
        if not batch.zip_file or batch.is_expired:
            return Response(
                {"detail": "The download is not available or has expired."},
                status=status.HTTP_410_GONE,
            )

        return FileResponse(
            batch.zip_file.open("rb"),
            as_attachment=True,
            filename=f"pixelflow-batch-{batch.id}.zip",
        )