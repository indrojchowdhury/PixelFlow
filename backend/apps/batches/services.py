import logging
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path

from celery import chord
from django.conf import settings
from django.core.files import File
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import get_valid_filename

from apps.images.models import Image

from .models import ProcessingBatch

logger = logging.getLogger(__name__)


def create_batch(user, album, images):
    batch = ProcessingBatch.objects.create(
        user=user, album=album, total_images=len(images)
    )
    batch.images.add(*images)
    return batch


def dispatch_batch(batch_id):
    """
    Run one task per image in parallel (header), then finalize the batch (callback).
    A broker failure is logged and must never break the upload response.
    """
    from .tasks import finalize_batch, process_batch_image

    try:
        image_ids = list(
            ProcessingBatch.objects.get(pk=batch_id).images.values_list("id", flat=True)
        )
        header = [process_batch_image.s(batch_id, image_id) for image_id in image_ids]
        chord(header)(finalize_batch.s(batch_id))
    except Exception:
        logger.exception("Could not dispatch batch %s; it stays pending.", batch_id)


def refresh_counts(batch_id):
    """
    Recompute counters from image statuses. The database is the source of truth,
    and recomputing (instead of incrementing) stays correct even if a task is retried.
    """
    stats = Image.objects.filter(batches__id=batch_id).aggregate(
        done=Count("id", filter=Q(status=Image.Status.COMPLETED)),
        failed=Count("id", filter=Q(status=Image.Status.FAILED)),
    )
    ProcessingBatch.objects.filter(pk=batch_id).update(
        processed_images=stats["done"], failed_images=stats["failed"]
    )
    return stats


def build_zip(batch):
    """Zip every processed version of the successful images, plus a failure report."""
    completed = batch.images.filter(status=Image.Status.COMPLETED).prefetch_related(
        "versions"
    )
    failed = list(batch.images.filter(status=Image.Status.FAILED))

    with tempfile.TemporaryFile() as tmp:
        # WebP is already compressed, so ZIP_STORED avoids wasted CPU
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED) as archive:
            for image in completed:
                # Names are sanitized so a hostile filename cannot escape the archive
                stem = get_valid_filename(Path(image.original_name).stem) or "image"
                folder = f"{image.id}_{stem}"
                for version in image.versions.all():
                    with version.file.open("rb") as source:
                        archive.writestr(
                            f"{folder}/{version.version_type}.webp", source.read()
                        )
            if failed:
                lines = ["These images could not be processed:", ""]
                lines += [f"- {img.original_name}: {img.error_message}" for img in failed]
                archive.writestr("failures.txt", "\n".join(lines))

        tmp.seek(0)
        if batch.zip_file:
            batch.zip_file.delete(save=False)
        batch.zip_file.save(f"{batch.id}.zip", File(tmp), save=False)

    batch.expires_at = timezone.now() + timedelta(hours=settings.BATCH_ZIP_TTL_HOURS)