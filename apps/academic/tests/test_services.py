from django.test import TestCase
from rest_framework.exceptions import ValidationError
from academic.models import Kelas, TahunAjaran
from academic.services import (
    kelas_create_service,
    siswa_create_service,
    siswa_update_service,
    tahun_ajaran_create_service,
)


class AcademicServicesTest(TestCase):
    def setUp(self):
        self.kelas = Kelas.objects.create(nama_kelas="X IPA 1")

    def test_tahun_ajaran_only_one_active(self):
        ta1 = tahun_ajaran_create_service(nama="2024/2025", is_aktif=True)
        ta2 = tahun_ajaran_create_service(nama="2025/2026", is_aktif=True)
        
        ta1.refresh_from_db()
        self.assertFalse(ta1.is_aktif)
        self.assertTrue(ta2.is_aktif)

    def test_siswa_create_and_update(self):
        siswa = siswa_create_service(
            nisn="12345678",
            nama="Budi Santoso",
            gender="L",
            angkatan=2025,
            kelas_id=self.kelas.id,
        )
        self.assertEqual(siswa.nama, "Budi Santoso")

        updated = siswa_update_service(instance=siswa, nama="Budi Pekerti")
        self.assertEqual(updated.nama, "Budi Pekerti")