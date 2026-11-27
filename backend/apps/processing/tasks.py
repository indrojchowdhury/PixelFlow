from celery import shared_task

from apps.images.models import Image

from .services import process_image


@shared_task(bind=True, acks_late=True)
def process_image_task(self, image_id):
    """
    Celery wrapper around the process_image service.

    acks_late: the message is removed from the queue only after the task
    finishes, so a worker crash does not lose the job. This is safe because
    process_image is idempotent.
    """
    already_done = Image.objects.filter(
        pk=image_id, status=Image.Status.COMPLETED
    ).exists()
    if already_done:
        # Duplicate delivery: nothing to do
        return {"image_id": image_id, "ok": True, "skipped": True}

    return process_image(image_id)