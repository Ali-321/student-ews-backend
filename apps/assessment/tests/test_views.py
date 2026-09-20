from datetime import date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment.models import NilaiSiswa, PresensiSiswa, PredictionResult

User = get_user_model()

class AssessmentViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="guru@school.id", 
            password="Password123!",
            role="GURU" 
        )
        self.client.force_authenticate(user=self.user)

        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.semester = Semester.objects.create(
            tahun_ajaran=self.ta,
            semester_ke=1,
            is_aktif=True,
            tanggal_mulai=date(2026, 1, 5),
            tanggal_selesai=date(2026, 6, 30),
        )
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(nisn="0012345678", nama="Budi", gender="L", kelas=self.kelas)
        self.mapel = MataPelajaran.objects.create(kode_mapel="MAT10", nama_mapel="Matematika")
        
        self.prediksi = PredictionResult.objects.create(
            siswa=self.siswa,
            mapel=self.mapel,
            semester=self.semester,
            minggu_ke=1,
            risk_score=PredictionResult.RiskChoices.MEDIUM,
            recommendation={"guru": "Pantau", "orangtua": "Bimbing", "siswa": "Belajar"}
        )

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
        self.assertTrue(get_response.data["success"])

    # DUA MOCK DENGAN DUA ARGUMEN DISINI
    @patch('assessment.services.transaction.on_commit', side_effect=lambda hook: hook())
    @patch('assessment.services.threading.Thread')
    def test_nilai_siswa_bulk_create_api(self, mock_thread, mock_on_commit):
        url = reverse("assessment:nilai-list-create")
        payload = {
            "mapel_id": self.mapel.id,
            "semester_id": self.semester.id,
            "tanggal_input": str(date.today()),
            "items": [
                {
                    "siswa_nisn": self.siswa.nisn,
                    "studytime": 5,
                    "evaluasi_list": [
                        {
                            "jenis_evaluasi": NilaiSiswa.EvaluasiChoices.QUIZ,
                            "nama_evaluasi": "Quiz 1",
                            "skor": 95.0
                        }
                    ]
                }
            ]
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_thread.called)
        
        get_response = self.client.get(f"{url}?siswa_nisn={self.siswa.nisn}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

    def test_presensi_bulk_create_api(self):
        url = reverse("assessment:presensi-list-bulk-create")
        payload = {
            "mapel_id": self.mapel.id,
            "semester_id": self.semester.id,
            "tanggal_mulai": str(date(2026, 1, 10)),
            "tanggal_akhir": str(date(2026, 1, 15)),
            "items": [
                {
                    "siswa_nisn": self.siswa.nisn,
                    "presensi_harian": [
                        {"tanggal": str(date(2026, 1, 12)), "status": PresensiSiswa.StatusChoices.HADIR}
                    ]
                }
            ]
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_status_choices_api(self):
        url = reverse("assessment:presensi-status-choices")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["data"]), 0)

    def test_siswa_risk_summary_list_api(self):
        url = reverse("assessment:siswa-risk-summary")
        response = self.client.get(f"{url}?kelas_id={self.kelas.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_detail_prediksi_ews_api(self):
        # MENGGUNAKAN NAMA RUTE YANG BENAR DARI URLS.PY (Tanpa Spasi)
        url = reverse("assessment:detail-prediksi-ews", kwargs={
            "siswa_nisn": self.siswa.nisn,
            "mapel_id": self.mapel.id,
            "minggu_ke": 1
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["risk_score"], PredictionResult.RiskChoices.MEDIUM)

    def test_detail_profil_siswa_ews_api(self):
        # MENGGUNAKAN NAMA RUTE YANG BENAR DARI URLS.PY
        url = reverse("assessment:detail-siswa-ews", kwargs={"siswa_nisn": self.siswa.nisn})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metrik_kinerja", response.data["data"])
        self.assertIn("analisis_ews", response.data["data"])