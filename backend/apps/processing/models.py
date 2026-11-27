from django.db import models

from apps.images.models import Image

from .presets import OUTPUT_EXTENSION, VersionType


def processed_upload_path(instance, filename):
    """Deterministic path: one file per (image, version type)."""
    image = instance.image
    return (
        f"processed/{image.user_id}/{image.id}/"
        f"{instance.version_type}.{OUTPUT_EXTENSION}"
    )


class ProcessedVersion(models.Model):
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_type = models.CharField(max_length=20, choices=VersionType.choices)
    file = models.FileField(upload_to=processed_upload_path, max_length=255)
    file_size = models.PositiveBigIntegerField()
    format = models.CharField(max_length=10)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["image_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["image", "version_type"],
                name="unique_version_type_per_image",
            )
        ]

    def __str__(self):
        return f"{self.image_id}:{self.version_type}"