from django.db import models


class VersionType(models.TextChoices):
    THUMBNAIL = "thumbnail", "Thumbnail"
    MEDIUM = "medium", "Medium"
    LARGE = "large", "Large"


# Longest side in pixels for each version. Images are never upscaled.
PRESETS = {
    VersionType.THUMBNAIL: 200,
    VersionType.MEDIUM: 800,
    VersionType.LARGE: 1600,
}

OUTPUT_FORMAT = "WEBP"
OUTPUT_EXTENSION = "webp"
OUTPUT_QUALITY = 80