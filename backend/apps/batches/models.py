from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.albums.models import Album
from apps.images.models import Image


def zip_upload_path(instance, filename):
    return f"zips/{instance.user_id}/{instance.id}.zip"


class ProcessingBatch(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="batches",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
    )
    images = models.ManyToManyField(Image, related_name="batches")
    total_images = models.PositiveIntegerField()
    processed_images = models.PositiveIntegerField(default=0)
    failed_images = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    zip_file = models.FileField(upload_to=zip_upload_path, max_length=255, blank=True)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return f"Batch {self.id} ({self.status})"

    @property
    def progress(self):
        if not self.total_images:
            return 0.0
        done = self.processed_images + self.failed_images
        return min(100.0, round(done / self.total_images * 100, 1))

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at < timezone.now()