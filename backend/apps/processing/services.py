import io
import logging
import time

from django.core.files.base import ContentFile
from PIL import Image as PILImage
from PIL import ImageOps

from apps.images.models import Image

from .models import ProcessedVersion
from .presets import OUTPUT_FORMAT, OUTPUT_QUALITY, PRESETS

logger = logging.getLogger(__name__)


def _normalize_mode(img):
    """Keep transparency when present, otherwise use plain RGB."""
    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    return img.convert("RGBA" if has_alpha else "RGB")


def render_version(base_image, max_side):
    """
    Resize a copy of base_image so its longest side is at most max_side,
    then encode it as WebP. Returns (bytes, width, height).
    """
    working = base_image.copy()
    # thumbnail() keeps aspect ratio and never upscales
    working.thumbnail((max_side, max_side), PILImage.Resampling.LANCZOS)

    buffer = io.BytesIO()
    working.save(buffer, format=OUTPUT_FORMAT, quality=OUTPUT_QUALITY, method=4)
    return buffer.getvalue(), working.width, working.height


def save_version(image, version_type, data, width, height):
    """
    Create or replace the processed file for one version type.
    Re-running on the same image replaces the output instead of duplicating it.
    """
    version = ProcessedVersion.objects.filter(
        image=image, version_type=version_type
    ).first()

    if version is not None and version.file:
        version.file.delete(save=False)
    if version is None:
        version = ProcessedVersion(image=image, version_type=version_type)

    version.format = OUTPUT_FORMAT
    version.width = width
    version.height = height
    version.file_size = len(data)
    version.file.save(f"{version_type}.webp", ContentFile(data), save=False)
    version.save()
    return version


def process_image(image_id):
    """
    Generate every preset version for one image.

    This function never raises. Any failure is recorded on the Image row
    (status=failed, error_message) and reported in the return value, so one
    bad image can never break a larger batch.
    """
    image = Image.objects.filter(pk=image_id).first()
    if image is None:
        return {"image_id": image_id, "ok": False, "error": "Image not found."}

    started = time.monotonic()
    image.status = Image.Status.PROCESSING
    image.error_message = ""
    image.save(update_fields=["status", "error_message"])

    try:
        with image.original_file.open("rb") as source_file:
            with PILImage.open(source_file) as source:
                source.load()
                base = _normalize_mode(ImageOps.exif_transpose(source))

        for version_type, max_side in PRESETS.items():
            data, width, height = render_version(base, max_side)
            save_version(image, version_type, data, width, height)

        image.status = Image.Status.COMPLETED
        image.processing_duration = round(time.monotonic() - started, 4)
        image.save(update_fields=["status", "processing_duration"])
        return {"image_id": image.id, "ok": True}

    except Exception as exc:
        logger.exception("Processing failed for image %s", image_id)
        image.status = Image.Status.FAILED
        image.error_message = str(exc)[:500]
        image.processing_duration = round(time.monotonic() - started, 4)
        image.save(update_fields=["status", "error_message", "processing_duration"])
        return {"image_id": image.id, "ok": False, "error": image.error_message}