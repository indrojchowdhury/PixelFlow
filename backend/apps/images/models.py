import uuid

from django.conf import settings
from django.db import models

from apps.albums.models import Album

EXTENSION_BY_FORMAT = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def original_upload_path(instance, filename):
    """Store originals under a random name so user-supplied names are never trusted."""
    extension = EXTENSION_BY_FORMAT.get(instance.format, "bin")
    return f"originals/{instance.user_id}/{uuid.uuid4().hex}.{extension}"


class Image(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="images",
    )
    original_file = models.ImageField(upload_to=original_upload_path, max_length=255)
    original_name = models.CharField(max_length=255)
    original_size = models.PositiveBigIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    format = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True)
    processing_duration = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["album", "status"]),
        ]

    def __str__(self):
        return f"{self.original_name} ({self.status})"