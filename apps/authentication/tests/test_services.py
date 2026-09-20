from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from authentication.models import User
from authentication.services import auth_login_service, user_create_service

class UserServiceTests(TestCase):
    def setUp(self):
        self.valid_email = "test@sekolah.com"
        self.valid_password = "securepassword123"
        self.user = User.objects.create_user(
            email=self.valid_email, 
            password=self.valid_password, 
            role=User.Role.GURU,
            first_name="Budi",
            last_name="Santoso"
        )

    # --- Pengujian Login Service ---
    def test_auth_login_service_success(self):
        """Memastikan login berhasil dan mengembalikan token JWT yang valid."""
        result = auth_login_service(email=self.valid_email, password=self.valid_password)
        
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertIn("user", result)
        self.assertEqual(result["user"]["email"], self.valid_email)
        self.assertEqual(result["user"]["role"], User.Role.GURU)

    def test_auth_login_service_wrong_password(self):
        """Memastikan sistem menolak kombinasi password yang salah."""
        with self.assertRaises(AuthenticationFailed) as context:
            auth_login_service(email=self.valid_email, password="wrongpassword")
        self.assertEqual(str(context.exception), "Email atau password salah.")

    def test_auth_login_service_inactive_user(self):
        """Memastikan user nonaktif tidak bisa login."""
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(AuthenticationFailed) as context:
            auth_login_service(email=self.valid_email, password=self.valid_password)
        self.assertEqual(str(context.exception), "Akun Anda sedang tidak aktif.")

    # --- Pengujian User Create Service ---
    def test_user_create_service_success(self):
        """Memastikan pembuatan user baru berfungsi dengan data yang valid."""
        new_user = user_create_service(
            email="baru@sekolah.com",
            password="password123",
            role=User.Role.SISWA,
            first_name="Siswa",
            last_name="Baru"
        )
        self.assertEqual(new_user.email, "baru@sekolah.com")
        self.assertEqual(new_user.role, User.Role.SISWA)
        self.assertTrue(new_user.check_password("password123"))

    def test_user_create_service_duplicate_email(self):
        """Memastikan pembuatan user ditolak jika email sudah terdaftar."""
        with self.assertRaises(ValidationError) as context:
            user_create_service(
                email=self.valid_email, # Email sudah dipakai di setUp
                password="password123",
                role=User.Role.SISWA
            )
        self.assertIn("email", context.exception.detail)

    def test_user_create_service_reject_superuser_role(self):
        """Memastikan role SUPERUSER tidak dapat digunakan di service ini."""
        with self.assertRaises(ValidationError) as context:
            user_create_service(
                email="hacker@sekolah.com",
                password="password123",
                role=User.Role.SUPERUSER
            )
        self.assertIn("role", context.exception.detail)