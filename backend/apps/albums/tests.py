from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Album

User = get_user_model()


class AlbumTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("user1", "u1@example.com", "StrongPass#2026")
        self.user2 = User.objects.create_user("user2", "u2@example.com", "StrongPass#2026")
        self.url = "/api/albums/"

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_album(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(self.url, {"name": "Trip", "description": "Cox's Bazar"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Album.objects.get().user, self.user1)

    def test_duplicate_name_same_user_rejected(self):
        self.client.force_authenticate(self.user1)
        self.client.post(self.url, {"name": "Trip"})
        response = self.client.post(self.url, {"name": "trip"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_name_different_user_allowed(self):
        Album.objects.create(user=self.user1, name="Trip")
        self.client.force_authenticate(self.user2)
        response = self.client.post(self.url, {"name": "Trip"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_shows_only_own_albums(self):
        Album.objects.create(user=self.user1, name="Mine")
        Album.objects.create(user=self.user2, name="Theirs")
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Mine")

    def test_cannot_access_other_users_album(self):
        album = Album.objects.create(user=self.user2, name="Theirs")
        self.client.force_authenticate(self.user1)
        detail_url = f"{self.url}{album.id}/"

        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            self.client.patch(detail_url, {"name": "Hacked"}).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Album.objects.filter(pk=album.pk).exists())

    def test_update_and_delete_own_album(self):
        album = Album.objects.create(user=self.user1, name="Old")
        self.client.force_authenticate(self.user1)
        detail_url = f"{self.url}{album.id}/"

        response = self.client.patch(detail_url, {"name": "New"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New")

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)