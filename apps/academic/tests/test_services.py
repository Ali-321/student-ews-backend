from django.test import TestCase
from rest_framework.exceptions import ValidationError
from academic.models import TahunAjaran, Kelas, Siswa
from academic.services import (
    tahun_ajaran_create_service,
    siswa_create_service,
    siswa_delete_service
)
from authentication.models import User

class AcademicServiceTests(TestCase):
    def setUp(self):
        self.kelas = Kelas.objects.create(nama_kelas="11 IPA 1")

    # --- Pengujian Mutasi Tahun Ajaran ---
    def test_tahun_ajaran_toggle_aktif_logic(self):
        """Memastikan hanya ada satu Tahun Ajaran yang aktif secara bersamaan."""
        ta1 = tahun_ajaran_create_service(nama="2024", is_aktif=True)
        self.assertTrue(ta1.is_aktif)

        # Buat TA kedua dengan status aktif
        ta2 = tahun_ajaran_create_service(nama="2025", is_aktif=True)
        self.assertTrue(ta2.is_aktif)

        # Refresh TA pertama dari DB, statusnya harus otomatis berubah jadi False
        ta1.refresh_from_db()
        self.assertFalse(ta1.is_aktif)

    # --- Pengujian Mutasi Siswa (Kompleksitas Tinggi) ---
    def test_siswa_create_service_success(self):
        """Siswa dibuat sekaligus melahirkan 2 entitas User (Siswa & Ortu) dengan email khusus."""
        siswa = siswa_create_service(
            nisn="998877",
            nama="Andi Wijaya",
            gender="L",
            kelas_id=self.kelas.id,
            first_name_orang_tua="Bapak",
            last_name_orang_tua="Wijaya"
        )

        self.assertEqual(siswa.nisn, "998877")
        
        # Pengecekan User Ortu
        self.assertIsNotNone(siswa.parent_user)
        self.assertEqual(siswa.parent_user.email, "bapak_998877@edupulse.parent.id")
        self.assertEqual(siswa.parent_user.role, User.Role.ORANGTUA)

        # Pengecekan User Siswa
        user_siswa = User.objects.filter(email="998877@edupulse.student.id").first()
        self.assertIsNotNone(user_siswa)
        self.assertEqual(user_siswa.role, User.Role.SISWA)
        
        # Pengecekan standar password format (nama_depan_ortu_hurufkecil+nisn)
        self.assertTrue(user_siswa.check_password("password123"))

    def test_siswa_create_service_duplicate_nisn(self):
        """Menolak pembuatan jika NISN sudah ada."""
        siswa_create_service(
            nisn="12345", nama="Test 1", gender="L", kelas_id=self.kelas.id, first_name_orang_tua="Ortu 1"
        )
        
        with self.assertRaises(ValidationError) as context:
            siswa_create_service(
                nisn="12345", nama="Test 2", gender="P", kelas_id=self.kelas.id, first_name_orang_tua="Ortu 2"
            )
        self.assertIn("nisn", context.exception.detail)

    def test_siswa_delete_service(self):
        """Menghapus Siswa harus mencabut (delete) akun Parent dan akun Student terkait."""
        siswa = siswa_create_service(
            nisn="55555", nama="Hapus Saya", gender="L", kelas_id=self.kelas.id, first_name_orang_tua="Pak Hapus"
        )
        
        email_ortu = siswa.parent_user.email
        email_siswa = "55555@edupulse.student.id"

        # Pastikan akun auth tercipta
        self.assertTrue(User.objects.filter(email=email_ortu).exists())
        self.assertTrue(User.objects.filter(email=email_siswa).exists())

        # Eksekusi Delete
        siswa_delete_service(instance=siswa)

        # Pastikan seluruh jejak terhapus
        self.assertFalse(Siswa.objects.filter(nisn="55555").exists())
        self.assertFalse(User.objects.filter(email=email_ortu).exists())
        self.assertFalse(User.objects.filter(email=email_siswa).exists())