from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed

from authentication.models import User
from authentication.services import auth_login_service


class AuthServicesTest(TestCase):
    def setUp(self):
        self.email = "test_service@example.com"
        self.password = "securepassword123"
        # Buat dummy user untuk testing
        self.user = User.objects.create_user(
            email=self.email, password=self.password
        )

    def test_auth_login_service_success(self):
        # Pengujian kredensial benar
        result = auth_login_service(email=self.email, password=self.password)
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertEqual(result["user"]["email"], self.email)

    def test_auth_login_service_wrong_password(self):
        # Pengujian kredensial salah
        with self.assertRaises(AuthenticationFailed):
            auth_login_service(email=self.email, password="wrongpassword")

    def test_auth_login_service_inactive_user(self):
        # Pengujian user yang di-nonaktifkan
        self.user.is_active = False
        self.user.save()
        
        with self.assertRaises(AuthenticationFailed):
            auth_login_service(email=self.email, password=self.password)