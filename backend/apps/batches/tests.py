import os
import shutil
import tempfile
import zipfile
from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from celery import signals as celery_signals
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.base import ContentFile
from django.db import close_old_connections
from django.test import override_settings
from django.utils import timezone
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from apps.albums.models import Album
from apps.images.models import Image
from config import celery_app

from .models import ProcessingBatch
from .services import create_batch
from .tasks import (
    cleanup_expired_batches,
    finalize_batch,
    process_batch_image,
    send_batch_email,
)

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()
LOCMEM = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


def png_bytes(size=(300, 200)):
    buffer = BytesIO()
    PILImage.new("RGB", size, color="red").save(buffer, format="PNG")
    return buffer.getvalue()


def _keep_db_connection_open(sender=None, **kwargs):
    """Celery's postrun hook closes DB connections, which breaks the test transaction."""


@override_settings(MEDIA_ROOT=TEMP_MEDIA, CACHES=LOCMEM)
class BatchTests(APITransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._celery_db_receivers = []
        cls._celery_close_database_methods = []
        for fixup in celery_app._fixups:
            if hasattr(fixup, "_close_database"):
                cls._celery_close_database_methods.append(
                    (fixup, fixup._close_database)
                )
                fixup._close_database = lambda: None
            if hasattr(fixup, "on_task_prerun"):
                celery_signals.task_prerun.disconnect(fixup.on_task_prerun)
                cls._celery_db_receivers.append(
                    (celery_signals.task_prerun, fixup.on_task_prerun)
                )
            if hasattr(fixup, "on_task_postrun"):
                celery_signals.task_postrun.disconnect(fixup.on_task_postrun)
                cls._celery_db_receivers.append(
                    (celery_signals.task_postrun, fixup.on_task_postrun)
                )

        for signal in (celery_signals.task_prerun, celery_signals.task_postrun):
            signal.connect(
                _keep_db_connection_open,
                dispatch_uid="batches_test_keep_db_connection_open",
                weak=False,
            )

    @classmethod
    def tearDownClass(cls):
        for signal in (celery_signals.task_prerun, celery_signals.task_postrun):
            signal.disconnect(dispatch_uid="batches_test_keep_db_connection_open")
        for signal, receiver in cls._celery_db_receivers:
            signal.connect(receiver)
        for fixup, close_database in cls._celery_close_database_methods:
            fixup._close_database = close_database
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        self.other = User.objects.create_user("user2", "u2@example.com", "StrongPass#2026")
        self.album = Album.objects.create(user=self.user, name="Test")

    def make_image(self, data=None, name="photo.png"):
        data = data if data is not None else png_bytes()
        image = Image(
            user=self.user,
            album=self.album,
            original_name=name,
            original_size=len(data),
            width=300,
            height=200,
            format="PNG",
        )
        image.original_file.save(name, ContentFile(data), save=False)
        image.save()
        return image

    def make_batch(self, images):
        return create_batch(self.user, self.album, images)

    def run_batch(self, batch):
        """Run the chord steps in-process, without a broker or a worker."""
        for image in batch.images.all():
            process_batch_image.apply(args=[batch.id, image.id]).get()
        with patch("apps.batches.tasks.send_batch_email.delay") as mock_email:
            finalize_batch.apply(args=[[], batch.id]).get()
        batch.refresh_from_db()
        return mock_email

    def test_full_flow_with_one_failed_image(self):
        batch = self.make_batch(
            [self.make_image(), self.make_image(), self.make_image(data=b"not an image")]
        )
        with self.assertLogs("apps.processing.services", level="ERROR"):
            mock_email = self.run_batch(batch)

        self.assertEqual(batch.status, ProcessingBatch.Status.COMPLETED)
        self.assertEqual(batch.processed_images, 2)
        self.assertEqual(batch.failed_images, 1)
        self.assertEqual(batch.progress, 100.0)
        self.assertIsNotNone(batch.expires_at)
        mock_email.assert_called_once_with(batch.id)

        with zipfile.ZipFile(batch.zip_file.path) as archive:
            names = archive.namelist()
        self.assertIn("failures.txt", names)
        self.assertEqual(sum(n.endswith("/thumbnail.webp") for n in names), 2)

    def test_finalize_is_idempotent(self):
        batch = self.make_batch([self.make_image()])
        self.run_batch(batch)
        zip_name = batch.zip_file.name

        with patch("apps.batches.tasks.send_batch_email.delay") as mock_email:
            result = finalize_batch.apply(args=[[], batch.id]).get()

        self.assertTrue(result["skipped"])
        mock_email.assert_not_called()
        batch.refresh_from_db()
        self.assertEqual(batch.zip_file.name, zip_name)

    def test_stuck_images_are_closed_as_failed(self):
        image = self.make_image()
        image.status = Image.Status.PROCESSING
        image.save(update_fields=["status"])
        batch = self.make_batch([image])

        self.run_batch_finalize_only(batch)

        image.refresh_from_db()
        self.assertEqual(image.status, Image.Status.FAILED)
        self.assertEqual(batch.status, ProcessingBatch.Status.FAILED)
        self.assertFalse(batch.zip_file)

    def run_batch_finalize_only(self, batch):
        with patch("apps.batches.tasks.send_batch_email.delay"):
            finalize_batch.apply(args=[[], batch.id]).get()
        batch.refresh_from_db()

    def test_progress_endpoint(self):
        batch = ProcessingBatch.objects.create(
            user=self.user, album=self.album, total_images=4,
            processed_images=1, failed_images=1,
        )
        self.client.force_authenticate(self.user)
        response = self.client.get(f"/api/batches/{batch.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["progress"], 50.0)
        self.assertFalse(response.data["download_available"])

    def test_other_users_batch_returns_404(self):
        batch = self.make_batch([self.make_image()])
        self.client.force_authenticate(self.other)
        self.assertEqual(
            self.client.get(f"/api/batches/{batch.id}/").status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client.get(f"/api/batches/{batch.id}/download/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_download_states(self):
        batch = self.make_batch([self.make_image()])
        self.client.force_authenticate(self.user)
        url = f"/api/batches/{batch.id}/download/"

        self.assertEqual(self.client.get(url).status_code, status.HTTP_409_CONFLICT)

        self.run_batch(batch)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(b"".join(response.streaming_content).startswith(b"PK"))
        response.close()

        batch.expires_at = timezone.now() - timedelta(hours=1)
        batch.save(update_fields=["expires_at"])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_410_GONE)

    def test_cleanup_removes_expired_zip(self):
        batch = self.make_batch([self.make_image()])
        self.run_batch(batch)
        path = batch.zip_file.path
        self.assertTrue(os.path.exists(path))

        batch.expires_at = timezone.now() - timedelta(hours=1)
        batch.save(update_fields=["expires_at"])
        result = cleanup_expired_batches.apply().get()

        batch.refresh_from_db()
        self.assertEqual(result["removed"], 1)
        self.assertFalse(batch.zip_file)
        self.assertFalse(os.path.exists(path))

    def test_email_is_sent_once(self):
        batch = self.make_batch([self.make_image()])
        self.run_batch(batch)

        send_batch_email.apply(args=[batch.id]).get()
        send_batch_email.apply(args=[batch.id]).get()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["u1@example.com"])
        batch.refresh_from_db()
        self.assertTrue(batch.email_sent)