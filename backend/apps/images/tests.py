import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image as PILImage
from rest_framework import status
from rest_framework.test import APITestCase

from apps.albums.models import Album
from apps.batches.models import ProcessingBatch

from .models import Image

User = get_user_model()
TEMP_MEDIA = tempfile.mkdtemp()


def make_image_file(name="photo.png", image_format="PNG", size=(50, 40)):
    buffer = BytesIO()
    PILImage.new("RGB", size, color="red").save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue())


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ImageTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user1 = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        self.user2 = User.objects.create_user("user2", "u2@example.com", "StrongPass#2026")
        self.album1 = Album.objects.create(user=self.user1, name="Mine")
        self.album2 = Album.objects.create(user=self.user2, name="Theirs")
        self.upload_url = "/api/images/upload/"
        self.list_url = "/api/images/"

    def upload(self, album, files):
        return self.client.post(
            self.upload_url,
            {"album": album.id, "files": files},
            format="multipart",
        )

    def test_requires_authentication(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.post(self.upload_url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_upload_success(self):
        self.client.force_authenticate(self.user1)
        files = [make_image_file("a.png"), make_image_file("b.jpg", "JPEG")]
        response = self.upload(self.album1, files)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(len(response.data["created"]), 2)
        self.assertEqual(response.data["rejected"], [])
        self.assertEqual(Image.objects.filter(user=self.user1).count(), 2)
        self.assertEqual(Image.objects.first().status, Image.Status.PENDING)

    def test_filename_is_randomized(self):
        self.client.force_authenticate(self.user1)
        self.upload(self.album1, [make_image_file("secret_name.png")])
        image = Image.objects.get()
        self.assertEqual(image.original_name, "secret_name.png")
        self.assertNotIn("secret_name", image.original_file.name)

    def test_fake_image_rejected(self):
        self.client.force_authenticate(self.user1)
        fake = SimpleUploadedFile("fake.jpg", b"this is not an image")
        response = self.upload(self.album1, [fake])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data["rejected"]), 1)
        self.assertEqual(Image.objects.count(), 0)

    def test_unsupported_format_rejected(self):
        self.client.force_authenticate(self.user1)
        gif = make_image_file("anim.gif", "GIF")
        response = self.upload(self.album1, [gif])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Image.objects.count(), 0)

    def test_partial_success(self):
        self.client.force_authenticate(self.user1)
        files = [make_image_file("ok.png"), SimpleUploadedFile("bad.png", b"garbage")]
        response = self.upload(self.album1, files)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(len(response.data["created"]), 1)
        self.assertEqual(len(response.data["rejected"]), 1)

    @override_settings(MAX_IMAGE_DIMENSION=100)
    def test_oversized_dimensions_rejected(self):
        self.client.force_authenticate(self.user1)
        big = make_image_file("big.png", size=(200, 50))
        response = self.upload(self.album1, [big])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_upload_to_other_users_album(self):
        self.client.force_authenticate(self.user1)
        response = self.upload(self.album2, [make_image_file()])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Image.objects.count(), 0)

    def test_list_shows_only_own_images(self):
        self.client.force_authenticate(self.user1)
        self.upload(self.album1, [make_image_file()])
        self.client.force_authenticate(self.user2)
        self.upload(self.album2, [make_image_file()])

        self.client.force_authenticate(self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_album(self):
        self.client.force_authenticate(self.user1)
        album_b = Album.objects.create(user=self.user1, name="Second")
        self.upload(self.album1, [make_image_file()])
        self.upload(album_b, [make_image_file(), make_image_file()])

        response = self.client.get(f"{self.list_url}?album={album_b.id}")
        self.assertEqual(response.data["count"], 2)

    def test_cannot_access_other_users_image(self):
        self.client.force_authenticate(self.user2)
        self.upload(self.album2, [make_image_file()])
        image = Image.objects.get()

        self.client.force_authenticate(self.user1)
        detail_url = f"{self.list_url}{image.id}/"
        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Image.objects.filter(pk=image.pk).exists())

    def test_delete_image_removes_file(self):
        self.client.force_authenticate(self.user1)
        self.upload(self.album1, [make_image_file()])
        image = Image.objects.get()
        file_path = image.original_file.path

        response = self.client.delete(f"{self.list_url}{image.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 0)

        import os
        self.assertFalse(os.path.exists(file_path))

    def test_album_image_count(self):
        self.client.force_authenticate(self.user1)
        self.upload(self.album1, [make_image_file(), make_image_file()])

        response = self.client.get("/api/albums/")
        self.assertEqual(response.data["results"][0]["image_count"], 2)

    def test_upload_creates_batch_and_dispatches_it(self):
        self.client.force_authenticate(self.user1)
        with patch("apps.images.views.dispatch_batch") as mock_dispatch:
            with self.captureOnCommitCallbacks(execute=True):
                response = self.upload(
                    self.album1, [make_image_file("a.png"), make_image_file("b.png")]
                )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        batch = ProcessingBatch.objects.get()
        self.assertEqual(response.data["batch_id"], batch.id)
        self.assertEqual(batch.total_images, 2)
        self.assertEqual(batch.images.count(), 2)
        mock_dispatch.assert_called_once_with(batch.id)

    def test_broker_failure_does_not_break_upload(self):
        self.client.force_authenticate(self.user1)
        with patch("apps.batches.services.chord", side_effect=ConnectionError("broker down")):
            with self.captureOnCommitCallbacks(execute=True):
                response = self.upload(self.album1, [make_image_file()])

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Image.objects.get().status, Image.Status.PENDING)
        self.assertEqual(ProcessingBatch.objects.get().status, ProcessingBatch.Status.PENDING)