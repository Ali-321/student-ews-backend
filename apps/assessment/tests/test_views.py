from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment.models import NilaiSiswa, PresensiSiswa

User = get_user_model()


class AssessmentViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="guru@school.id", password="Password123!")
        self.client.force_authenticate(user=self.user)

        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.semester = Semester.objects.create(tahun_ajaran=self.ta, semester_ke=1, is_aktif=True)
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(nisn="0012345678", nama="Budi", gender="L", kelas=self.kelas)
        self.mapel = MataPelajaran.objects.create(kode_mapel="MAT10", nama_mapel="Matematika")

    def test_histori_studytime_list_create_api(self):
        url = reverse("assessment:studytime-list-create")
        payload = {
            "siswa_nisn": self.siswa.nisn,
            "mapel_id": self.mapel.id,
            "semester_id": self.semester.id,
            "minggu_ke": 1,
            "studytime": 4
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        get_response = self.client.get(f"{url}?siswa_nisn={self.siswa.nisn}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data["data"]), 1)

    def test_nilai_siswa_list_create_api(self):
        url = reverse("assessment:nilai-list-create")
        payload = {
            "siswa_nisn": self.siswa.nisn,
            "mapel_id": self.mapel.id,
            "semester_id": self.semester.id,
            "minggu_ke": 1,
            "jenis_evaluasi": NilaiSiswa.EvaluasiChoices.QUIZ,
            "nama_evaluasi": "Quiz 1",
            "skor": 95.0,
            "is_terlambat": False
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_presensi_bulk_create_api(self):
        url = reverse("assessment:presensi-list-bulk-create")
        payload = {
            "mapel_id": self.mapel.id,
            "semester_id": self.semester.id,
            "minggu_ke": 1,
            "tanggal": str(date.today()),
            "items": [{"siswa_nisn": self.siswa.nisn, "status": PresensiSiswa.StatusChoices.HADIR}]
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ringkasan_akademik_siswa_api(self):
        url = reverse("assessment:siswa-ringkasan-akademik", kwargs={"siswa_nisn": self.siswa.nisn})
        response = self.client.get(f"{url}?semester_id={self.semester.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rata_rata_nilai", response.data["data"])