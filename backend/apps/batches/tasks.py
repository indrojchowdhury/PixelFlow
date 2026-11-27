import logging
from smtplib import SMTPException

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from apps.dashboard.cache import invalidate_dashboard
from apps.images.models import Image
from apps.processing.services import process_image

from .models import ProcessingBatch
from .services import build_zip, refresh_counts

logger = logging.getLogger(__name__)


@shared_task(bind=True, acks_late=True)
def process_batch_image(self, batch_id, image_id):
    """
    Header task of the chord. It must never raise: if one header task fails,
    Celery would skip the chord callback and the whole batch would hang.
    """
    try:
        ProcessingBatch.objects.filter(
            pk=batch_id, status=ProcessingBatch.Status.PENDING
        ).update(status=ProcessingBatch.Status.PROCESSING)

        already_done = Image.objects.filter(
            pk=image_id, status=Image.Status.COMPLETED
        ).exists()
        if already_done:
            result = {"image_id": image_id, "ok": True, "skipped": True}
        else:
            result = process_image(image_id)

        refresh_counts(batch_id)
        return result
    except Exception as exc:
        logger.exception("Unexpected error for image %s in batch %s", image_id, batch_id)
        return {"image_id": image_id, "ok": False, "error": str(exc)[:200]}


@shared_task(bind=True, acks_late=True)
def finalize_batch(self, results, batch_id):
    """Chord callback: runs once, after every image task has finished."""
    batch = ProcessingBatch.objects.filter(pk=batch_id).first()
    if batch is None or batch.completed_at is not None:
        return {"batch_id": batch_id, "skipped": True}

    # Anything that never reached a final state is closed as failed
    Image.objects.filter(
        batches__id=batch_id,
        status__in=[Image.Status.PENDING, Image.Status.PROCESSING],
    ).update(status=Image.Status.FAILED, error_message="Processing did not finish.")

    stats = refresh_counts(batch_id)
    batch.refresh_from_db()

    if stats["done"] > 0:
        build_zip(batch)
        batch.status = ProcessingBatch.Status.COMPLETED
    else:
        batch.status = ProcessingBatch.Status.FAILED

    batch.completed_at = timezone.now()
    batch.save()
    invalidate_dashboard(batch.user_id)

    try:
        send_batch_email.delay(batch.id)
    except Exception:
        logger.exception("Could not queue the email for batch %s", batch.id)

    return {"batch_id": batch.id, "status": batch.status}


@shared_task(
    bind=True,
    autoretry_for=(SMTPException, OSError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def send_batch_email(self, batch_id):
    """
    Retries cover our own infrastructure failures (SMTP down), with exponential backoff.
    email_sent makes it safe against duplicate delivery.
    """
    batch = ProcessingBatch.objects.select_related("user").filter(pk=batch_id).first()
    if batch is None or batch.email_sent or not batch.user.email:
        return

    if batch.status == ProcessingBatch.Status.COMPLETED:
        subject = f"Your PixelFlow batch #{batch.id} is ready"
        body = (
            f"{batch.processed_images} of {batch.total_images} images were processed "
            f"({batch.failed_images} failed).\n"
            f"Your ZIP is available until {batch.expires_at:%Y-%m-%d %H:%M}."
        )
    else:
        subject = f"Your PixelFlow batch #{batch.id} failed"
        body = "None of the images in this batch could be processed."

    send_mail(subject, body, None, [batch.user.email])
    batch.email_sent = True
    batch.save(update_fields=["email_sent"])


@shared_task
def cleanup_expired_batches():
    """Celery Beat task: delete ZIP files whose download window has passed."""
    expired = ProcessingBatch.objects.filter(expires_at__lt=timezone.now()).exclude(
        zip_file=""
    )
    removed = 0
    for batch in expired:
        batch.zip_file.delete(save=False)
        batch.zip_file = ""
        batch.save(update_fields=["zip_file"])
        removed += 1
    return {"removed": removed}