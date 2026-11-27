from django.db.models import Avg, Count, Q, Sum

from apps.albums.models import Album
from apps.batches.models import ProcessingBatch
from apps.batches.serializers import BatchSerializer
from apps.images.models import Image
from apps.processing.models import ProcessedVersion
from apps.processing.presets import VersionType


def build_dashboard(user):
    """
    Everything is computed with aggregate queries, never by looping over rows.
    "Storage saved" compares the original with the large WebP version of each
    completed image, so the number is well defined.
    """
    completed = Q(status=Image.Status.COMPLETED)
    image_stats = Image.objects.filter(user=user).aggregate(
        total=Count("id"),
        completed=Count("id", filter=completed),
        failed=Count("id", filter=Q(status=Image.Status.FAILED)),
        in_progress=Count(
            "id",
            filter=Q(status__in=[Image.Status.PENDING, Image.Status.PROCESSING]),
        ),
        original_bytes=Sum("original_size", filter=completed),
        average_seconds=Avg("processing_duration", filter=completed),
    )
    processed_bytes = (
        ProcessedVersion.objects.filter(
            image__user=user,
            image__status=Image.Status.COMPLETED,
            version_type=VersionType.LARGE,
        ).aggregate(total=Sum("file_size"))["total"]
        or 0
    )
    original_bytes = image_stats["original_bytes"] or 0
    average = image_stats["average_seconds"]

    recent = ProcessingBatch.objects.filter(user=user)[:10]

    return {
        "total_albums": Album.objects.filter(user=user).count(),
        "total_images": image_stats["total"],
        "completed_images": image_stats["completed"],
        "failed_images": image_stats["failed"],
        "in_progress_images": image_stats["in_progress"],
        "total_batches": ProcessingBatch.objects.filter(user=user).count(),
        "original_bytes": original_bytes,
        "processed_bytes": processed_bytes,
        "saved_bytes": original_bytes - processed_bytes,
        "average_processing_seconds": round(average, 3) if average is not None else None,
        "recent_batches": list(BatchSerializer(recent, many=True).data),
    }