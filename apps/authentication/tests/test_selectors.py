from django.test import TestCase
from authentication.models import User
from authentication.selectors import user_list_selector, user_get_me_selector

class UserSelectorTests(TestCase):
    def setUp(self):
        # Setup data awal (Seeding)
        self.admin = User.objects.create_user(
            email="admin@sekolah.com", password="password123", role=User.Role.ADMIN
        )
        self.siswa1 = User.objects.create_user(
            email="siswa1@sekolah.com", password="password123", role=User.Role.SISWA
        )
        self.siswa2 = User.objects.create_user(
            email="siswa2@sekolah.com", password="password123", role=User.Role.SISWA
        )

    def test_user_list_selector_without_filter(self):
        """Memastikan selector mengambil seluruh user tanpa filter dan diurutkan descending."""
        users = user_list_selector()
        self.assertEqual(users.count(), 3)
        # user terakhir dibuat akan ada di urutan pertama (karena -date_joined)
        self.assertEqual(users.first().email, self.siswa2.email)

    def test_user_list_selector_with_role_filter(self):
        """Memastikan selector merespons filter role dengan benar."""
        siswa_users = user_list_selector(role=User.Role.SISWA)
        self.assertEqual(siswa_users.count(), 2)
        
        admin_users = user_list_selector(role=User.Role.ADMIN)
        self.assertEqual(admin_users.count(), 1)
        self.assertEqual(admin_users.first().email, "admin@sekolah.com")

        guru_users = user_list_selector(role=User.Role.GURU)
        self.assertEqual(guru_users.count(), 0)

    def test_user_get_me_selector(self):
        """Memastikan selector mengembalikan instance user yang tepat."""
        user = user_get_me_selector(user=self.admin)
        self.assertEqual(user.email, self.admin.email)
        self.assertEqual(user.role, User.Role.ADMIN)