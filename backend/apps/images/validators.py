from django.conf import settings
from PIL import Image as PILImage
from PIL import UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageValidationError(Exception):
    """Raised when an uploaded file is not an acceptable image."""


def inspect_image(uploaded_file):
    """
    Validate an uploaded file by its real content (not its extension).

    Returns a dict with format, width, height and size.
    Raises ImageValidationError with a user-friendly message on failure.
    """
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if uploaded_file.size == 0:
        raise ImageValidationError("File is empty.")
    if uploaded_file.size > max_bytes:
        raise ImageValidationError(
            f"File is larger than {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    try:
        uploaded_file.seek(0)
        with PILImage.open(uploaded_file) as img:
            image_format = img.format
            width, height = img.size

            if image_format not in ALLOWED_FORMATS:
                raise ImageValidationError(
                    "Unsupported format. Allowed formats: JPEG, PNG, WEBP."
                )
            if max(width, height) > settings.MAX_IMAGE_DIMENSION:
                raise ImageValidationError(
                    f"Image dimensions exceed {settings.MAX_IMAGE_DIMENSION}px."
                )

            # verify() checks file integrity without decoding the full image
            img.verify()
    except ImageValidationError:
        raise
    except (
        UnidentifiedImageError,
        PILImage.DecompressionBombError,
        OSError,
        SyntaxError,
        ValueError,
    ):
        raise ImageValidationError("File is not a valid image.")
    finally:
        uploaded_file.seek(0)

    return {
        "format": image_format,
        "width": width,
        "height": height,
        "size": uploaded_file.size,
    }