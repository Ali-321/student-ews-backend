from django.test import TestCase
from rest_framework.exceptions import NotFound
from academic.models import TahunAjaran, Kelas, Siswa
from academic.selectors import (
    tahun_ajaran_get_selector,
    siswa_list_selector
)
from authentication.models import User

class AcademicSelectorTests(TestCase):
    def setUp(self):
        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.kelas_a = Kelas.objects.create(nama_kelas="10 A")
        self.kelas_b = Kelas.objects.create(nama_kelas="10 B")
        
        self.ortu = User.objects.create_user(email="ortu@test.id", password="123", role=User.Role.ORANGTUA)
        self.siswa1 = Siswa.objects.create(
            nisn="111", nama="Budi Santoso", gender=Siswa.GenderChoices.LAKI_LAKI, 
            kelas=self.kelas_a, parent_user=self.ortu
        )
        self.siswa2 = Siswa.objects.create(
            nisn="222", nama="Siti Aminah", gender=Siswa.GenderChoices.PEREMPUAN, 
            kelas=self.kelas_b, parent_user=self.ortu
        )

    def test_tahun_ajaran_get_selector_success(self):
        ta = tahun_ajaran_get_selector(id=self.ta.id)
        self.assertEqual(ta.nama, "2025/2026")

    def test_tahun_ajaran_get_selector_not_found(self):
        with self.assertRaises(NotFound):
            tahun_ajaran_get_selector(id=999)

    def test_siswa_list_selector_with_kelas_filter(self):
        qs = siswa_list_selector(kelas_id=self.kelas_a.id)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().nisn, "111")

    def test_siswa_list_selector_with_search_filter(self):
        # Pencarian parsial (case-insensitive) pada nama
        qs_nama = siswa_list_selector(search="siti")
        self.assertEqual(qs_nama.count(), 1)
        self.assertEqual(qs_nama.first().nisn, "222")

        # Pencarian pada NISN
        qs_nisn = siswa_list_selector(search="111")
        self.assertEqual(qs_nisn.count(), 1)