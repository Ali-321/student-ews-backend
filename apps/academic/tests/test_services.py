from django.test import TestCase
from rest_framework.exceptions import ValidationError
from academic.models import Kelas, TahunAjaran
from academic.services import (
    siswa_create_service,
    siswa_update_service,
    tahun_ajaran_create_service,
)
from academic.models import Semester, TahunAjaran

from datetime import date

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
            kelas_id=self.kelas.id,
        )
        self.assertEqual(siswa.nama, "Budi Santoso")

        updated = siswa_update_service(instance=siswa, nama="Budi Pekerti")
        self.assertEqual(updated.nama, "Budi Pekerti")

class SemesterModelTest(TestCase):
    def setUp(self):
        self.ta = TahunAjaran.objects.create(nama="2026/2027", is_aktif=True)
        # Semester mulai Senin, 13 Juli 2026
        self.semester = Semester.objects.create(
            tahun_ajaran=self.ta,
            semester_ke=1,
            is_aktif=True,
            tanggal_mulai=date(2026, 7, 13),
            tanggal_selesai=date(2026, 12, 31)
        )

    def test_get_minggu_ke_minggu_pertama(self):
        # Rabu di minggu yang sama -> Minggu ke-1
        target_date = date(2026, 7, 15)
        self.assertEqual(self.semester.get_minggu_ke(target_date), 1)

    def test_get_minggu_ke_minggu_selanjutnya(self):
        # Tepat 2 minggu setelah tanggal mulai (27 Juli 2026) -> Minggu ke-3
        target_date = date(2026, 7, 27)
        self.assertEqual(self.semester.get_minggu_ke(target_date), 3)

    def test_get_minggu_ke_sebelum_tanggal_mulai(self):
        # Tanggal sebelum semester berjalan -> Default kembali ke Minggu ke-1
        target_date = date(2026, 7, 1)
        self.assertEqual(self.semester.get_minggu_ke(target_date), 1)
