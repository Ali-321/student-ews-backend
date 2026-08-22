# apps/authentication/tests/test_views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User


class AuthViewsTest(APITestCase):
    def setUp(self):
        self.email = "test_view@example.com"
        self.password = "viewpassword123"
        self.user = User.objects.create_user(
            email=self.email, 
            password=self.password, 
            role=User.Role.ADMIN
        )
        # Pastikan nama 'login' dan 'me' sesuai dengan name="..." di urls.py
        self.login_url = reverse("login")
        self.me_url = reverse("me")

    def test_login_api_success(self):
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access_token", response.data["data"])

    def test_login_api_validation_error(self):
        # Kirim request tanpa email dan password
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_api_success(self):
        # Login terlebih dahulu untuk mendapatkan token
        login_resp = self.client.post(
            self.login_url, {"email": self.email, "password": self.password}
        )
        token = login_resp.data["data"]["access_token"]

        # Request ke endpoint me dengan menyertakan token di Header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], self.email)

    def test_me_api_unauthorized(self):
        # Request ke endpoint me TANPA token
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_by_admin_success(self):
        self.client.force_authenticate(user=self.user) # admin user
        payload = {
            "email": "guru1@school.id",
            "password": "Password123!",
            "role": "GURU"
        }
        response = self.client.post(reverse("user_list_create"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["email"], "guru1@school.id")
        
    def test_create_user_forbidden_for_non_admin(self):
        regular_user = User.objects.create_user(email="siswa@school.id", password="password", role=User.Role.SISWA)
        self.client.force_authenticate(user=regular_user)
        
        response = self.client.post(reverse("user_list_create"), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

