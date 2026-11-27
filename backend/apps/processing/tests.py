import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage

from apps.albums.models import Album
from apps.images.models import Image

from .models import ProcessedVersion
from .services import process_image

def test_corrupt_image_is_marked_failed_without_raising(self):
        image = self.create_image(data=b"this is not an image")

        with self.assertLogs("apps.processing.services", level="ERROR"):
            result = process_image(image.id)

        self.assertFalse(result["ok"])
        image.refresh_from_db()
        self.assertEqual(image.status, Image.Status.FAILED)
        self.assertTrue(image.error_message)
        self.assertEqual(ProcessedVersion.objects.filter(image=image).count(), 0)

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()


def make_bytes(size=(3000, 2000), mode="RGB", image_format="PNG"):
    buffer = BytesIO()
    color = (255, 0, 0, 128) if mode == "RGBA" else "red"
    PILImage.new(mode, size, color=color).save(buffer, format=image_format)
    return buffer.getvalue()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProcessingTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        self.album = Album.objects.create(user=self.user, name="Test")

    def create_image(self, data=None, width=3000, height=2000):
        data = data if data is not None else make_bytes((width, height))
        image = Image(
            user=self.user,
            album=self.album,
            original_name="photo.png",
            original_size=len(data),
            width=width,
            height=height,
            format="PNG",
        )
        image.original_file.save("photo.png", ContentFile(data), save=False)
        image.save()
        return image

    def test_creates_three_versions_with_correct_sizes(self):
        image = self.create_image()
        result = process_image(image.id)

        self.assertTrue(result["ok"])
        versions = {v.version_type: v for v in ProcessedVersion.objects.filter(image=image)}
        self.assertEqual(set(versions), {"thumbnail", "medium", "large"})
        self.assertEqual(max(versions["thumbnail"].width, versions["thumbnail"].height), 200)
        self.assertEqual(max(versions["medium"].width, versions["medium"].height), 800)
        self.assertEqual(max(versions["large"].width, versions["large"].height), 1600)
        for version in versions.values():
            self.assertEqual(version.format, "WEBP")
            self.assertTrue(os.path.exists(version.file.path))

    def test_aspect_ratio_preserved(self):
        image = self.create_image()
        process_image(image.id)
        medium = ProcessedVersion.objects.get(image=image, version_type="medium")
        self.assertEqual((medium.width, medium.height), (800, 533))

    def test_small_image_is_not_upscaled(self):
        image = self.create_image(width=100, height=80)
        process_image(image.id)
        large = ProcessedVersion.objects.get(image=image, version_type="large")
        self.assertEqual((large.width, large.height), (100, 80))

    def test_status_and_duration_recorded(self):
        image = self.create_image(width=300, height=200)
        process_image(image.id)
        image.refresh_from_db()
        self.assertEqual(image.status, Image.Status.COMPLETED)
        self.assertIsNotNone(image.processing_duration)
        self.assertEqual(image.error_message, "")

    def test_idempotent_rerun_does_not_duplicate(self):
        image = self.create_image(width=300, height=200)
        process_image(image.id)
        process_image(image.id)

        self.assertEqual(ProcessedVersion.objects.filter(image=image).count(), 3)
        folder = os.path.join(TEMP_MEDIA, "processed", str(self.user.id), str(image.id))
        self.assertEqual(len(os.listdir(folder)), 3)

    def test_corrupt_image_is_marked_failed_without_raising(self):
        image = self.create_image(data=b"this is not an image")
        result = process_image(image.id)

        self.assertFalse(result["ok"])
        image.refresh_from_db()
        self.assertEqual(image.status, Image.Status.FAILED)
        self.assertTrue(image.error_message)
        self.assertEqual(ProcessedVersion.objects.filter(image=image).count(), 0)

    def test_missing_image_returns_not_ok(self):
        result = process_image(999999)
        self.assertFalse(result["ok"])

    def test_transparent_png_is_supported(self):
        data = make_bytes((400, 300), mode="RGBA")
        image = self.create_image(data=data, width=400, height=300)
        result = process_image(image.id)
        self.assertTrue(result["ok"])

    def test_deleting_image_removes_processed_files(self):
        image = self.create_image(width=300, height=200)
        process_image(image.id)
        paths = [v.file.path for v in ProcessedVersion.objects.filter(image=image)]
        self.assertEqual(len(paths), 3)

        image.delete()
        for path in paths:
            self.assertFalse(os.path.exists(path))