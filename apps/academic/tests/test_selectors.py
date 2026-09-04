from django.test import TestCase
from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran
from academic.selectors import (
    kelas_list_selector,
    mapel_list_selector,
    semester_list_selector,
    siswa_list_selector,
    tahun_ajaran_list_selector,
)
from authentication.models import User


class AcademicSelectorsTest(TestCase):
    def setUp(self):
        # Setup User Guru & Parent
        self.guru = User.objects.create_user(email="guru@school.id", password="password", role=User.Role.GURU)
        self.parent = User.objects.create_user(email="parent@school.id", password="password", role=User.Role.ORANGTUA)

        # Setup Academic Base Data
        self.ta1 = TahunAjaran.objects.create(nama="2024/2025", is_aktif=False)
        self.ta2 = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)

        self.semester = Semester.objects.create(tahun_ajaran=self.ta2, semester_ke=1, is_aktif=True)
        self.kelas_a = Kelas.objects.create(nama_kelas="10 IPA 1", wali_kelas=self.guru)
        self.kelas_b = Kelas.objects.create(nama_kelas="10 IPA 2")

        self.mapel = MataPelajaran.objects.create(kode_mapel="MATH10", nama_mapel="Matematika", pengajar=self.guru)

        # Setup Siswa
        self.siswa_1 = Siswa.objects.create(
            nisn="1001",
            nama="Budi",
            gender="L",
         
            kelas=self.kelas_a,
            parent_user=self.parent,
        )
        self.siswa_2 = Siswa.objects.create(
            nisn="1002",
            nama="Andi",
            gender="L",
        
            kelas=self.kelas_b,
        )

    def test_tahun_ajaran_list_selector_ordering(self):
        qs = tahun_ajaran_list_selector()
        self.assertEqual(qs.count(), 2)
        # Dipastikan urut dari ID terbesar (-id)
        self.assertEqual(qs.first().id, self.ta2.id)

    def test_semester_list_selector(self):
        qs = semester_list_selector()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().tahun_ajaran.nama, "2025/2026")

    def test_kelas_and_mapel_list_selectors(self):
        self.assertEqual(kelas_list_selector().count(), 2)
        self.assertEqual(mapel_list_selector().count(), 1)

    def test_siswa_list_selector_without_filters(self):
        qs = siswa_list_selector()
        self.assertEqual(qs.count(), 2)
        # Dipastikan urut berdasarkan nama (Andi -> Budi)
        self.assertEqual(qs.first().nama, "Andi")

    def test_siswa_list_selector_filter_by_kelas(self):
        qs = siswa_list_selector(kelas_id=self.kelas_a.id)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().nisn, "1001")

    def test_siswa_list_selector_combined_filters(self):
        qs = siswa_list_selector(kelas_id=self.kelas_a.id)
        self.assertEqual(qs.count(), 0)