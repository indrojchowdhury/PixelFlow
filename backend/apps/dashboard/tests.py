import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test import override_settings
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITestCase

from apps.albums.models import Album
from apps.images.models import Image
from apps.processing.models import ProcessedVersion
from apps.processing.services import process_image

from .cache import invalidate_dashboard

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()
LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
URL = "/api/dashboard/"


@override_settings(MEDIA_ROOT=TEMP_MEDIA, CACHES=LOCMEM)
class DashboardTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        self.album = Album.objects.create(user=self.user, name="Test")

    def make_image(self):
        buffer = BytesIO()
        PILImage.new("RGB", (1200, 900), color="blue").save(buffer, format="PNG")
        data = buffer.getvalue()
        image = Image(
            user=self.user, album=self.album, original_name="p.png",
            original_size=len(data), width=1200, height=900, format="PNG",
        )
        image.original_file.save("p.png", ContentFile(data), save=False)
        image.save()
        return image

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats(self):
        done = self.make_image()
        self.make_image()  # stays pending
        process_image(done.id)
        done.refresh_from_db()
        large = ProcessedVersion.objects.get(image=done, version_type="large")

        self.client.force_authenticate(self.user)
        data = self.client.get(URL).data

        self.assertEqual(data["total_albums"], 1)
        self.assertEqual(data["total_images"], 2)
        self.assertEqual(data["completed_images"], 1)
        self.assertEqual(data["in_progress_images"], 1)
        self.assertEqual(data["failed_images"], 0)
        self.assertEqual(data["original_bytes"], done.original_size)
        self.assertEqual(data["processed_bytes"], large.file_size)
        self.assertEqual(data["saved_bytes"], done.original_size - large.file_size)
        self.assertIsNotNone(data["average_processing_seconds"])

    def test_cache_hit_then_invalidation(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get(URL)["X-Cache"], "MISS")
        self.assertEqual(self.client.get(URL)["X-Cache"], "HIT")
        invalidate_dashboard(self.user.id)
        self.assertEqual(self.client.get(URL)["X-Cache"], "MISS")