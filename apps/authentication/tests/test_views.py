from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewTests(APITestCase):
    def setUp(self):
       
        self.url_user_list_create = "/api/v1/auth/users/"
        self.url_user_me = "/api/v1/auth/me/"
        self.url_auth_login = "/api/v1/auth/login/"
        self.url_auth_refresh = "/api/v1/auth/refresh/"

        # Setup User Admin
        self.admin_user = User.objects.create_user(
            email="admin@sekolah.com", password="password123", role=User.Role.ADMIN
        )
        # Setup User Biasa (Siswa)
        self.siswa_user = User.objects.create_user(
            email="siswa@sekolah.com", password="password123", role=User.Role.SISWA
        )

    def get_auth_token(self, user):
        """Helper method untuk menghasilkan token JWT untuk request."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    # --- Pengujian Endpoint List & Create User (IsAdminRole) ---
    def test_user_list_api_as_admin_success(self):
        """Admin berhasil mengakses daftar user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.admin_user)}')
        response = self.client.get(self.url_user_list_create)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2) # Ada 2 user di database saat ini

    def test_user_list_api_as_siswa_forbidden(self):
        """Siswa (bukan Admin) diblokir saat mencoba melihat daftar user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.siswa_user)}')
        response = self.client.get(self.url_user_list_create)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_api_as_admin_success(self):
        """Admin berhasil membuat user baru melalui API POST."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.admin_user)}')
        payload = {
            "email": "guru@sekolah.com",
            "password": "password123",
            "role": User.Role.GURU,
            "first_name": "Pak",
            "last_name": "Guru"
        }
        response = self.client.post(self.url_user_list_create, data=payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="guru@sekolah.com").exists())

    # --- Pengujian Endpoint Me (IsAuthenticated) ---
    def test_me_api_success(self):
        """Mendapatkan profil diri sendiri dengan token yang valid."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.siswa_user)}')
        response = self.client.get(self.url_user_me)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], self.siswa_user.email)

    def test_me_api_unauthorized(self):
        """Permintaan tanpa Bearer Token akan ditolak."""
        response = self.client.get(self.url_user_me)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Pengujian Endpoint Auth (Login & Refresh) ---
    def test_login_api_success(self):
        """Login API mengembalikan JWT Token."""
        payload = {"email": "admin@sekolah.com", "password": "password123"}
        response = self.client.post(self.url_auth_login, data=payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data["data"])
        self.assertIn("refresh_token", response.data["data"])

    def test_token_refresh_api_success(self):
        """Refresh token API memvalidasi refresh token dan mengembalikan access token baru."""
        # Login dulu untuk dapat refresh token valid
        refresh_token = str(RefreshToken.for_user(self.admin_user))
        
        payload = {"refresh": refresh_token}
        response = self.client.post(self.url_auth_refresh, data=payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data["data"])

    def test_token_refresh_api_invalid(self):
        """Refresh token API menolak token yang ngawur atau kadaluwarsa."""
        payload = {"refresh": "token-yang-tidak-valid-123"}
        response = self.client.post(self.url_auth_refresh, data=payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])