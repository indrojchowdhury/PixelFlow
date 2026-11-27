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
from .tasks import process_image_task

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ProcessImageTaskTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        user = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        album = Album.objects.create(user=user, name="Test")

        buffer = BytesIO()
        PILImage.new("RGB", (400, 300), color="red").save(buffer, format="PNG")
        data = buffer.getvalue()

        self.image = Image(
            user=user,
            album=album,
            original_name="photo.png",
            original_size=len(data),
            width=400,
            height=300,
            format="PNG",
        )
        self.image.original_file.save("photo.png", ContentFile(data), save=False)
        self.image.save()

    def test_task_processes_image(self):
        # apply() runs the task in-process, so no broker or worker is needed
        result = process_image_task.apply(args=[self.image.id]).get()

        self.assertTrue(result["ok"])
        self.image.refresh_from_db()
        self.assertEqual(self.image.status, Image.Status.COMPLETED)
        self.assertEqual(ProcessedVersion.objects.filter(image=self.image).count(), 3)

    def test_task_skips_already_completed_image(self):
        process_image_task.apply(args=[self.image.id]).get()
        result = process_image_task.apply(args=[self.image.id]).get()

        self.assertTrue(result["skipped"])
        self.assertEqual(ProcessedVersion.objects.filter(image=self.image).count(), 3)