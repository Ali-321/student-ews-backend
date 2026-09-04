import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase

from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran
from apps.dashboard.selectors import get_dashboard_summary, get_school_analytics
from assessment.models import NilaiSiswa, PredictionResult, PresensiSiswa

User = get_user_model()


class DashboardSelectorsTestCase(TestCase):

    def setUp(self):
        # 1. User Setup
        self.user = User.objects.create_user(
            email="guru@example.com",
            password="password123",
            role=User.Role.GURU,
        )

        # 2. Academic Master Data Setup
        self.tahun_ajaran = TahunAjaran.objects.create(
            nama="2025/2026",
            is_aktif=True,
        )
        self.semester = Semester.objects.create(
            tahun_ajaran=self.tahun_ajaran,
            semester_ke=Semester.SemesterChoices.GANJIL,
            is_aktif=True,
        )
        self.kelas_a = Kelas.objects.create(
            nama_kelas="X IPA 1",
            wali_kelas=self.user,
        )
        self.mapel_math = MataPelajaran.objects.create(
            kode_mapel="MTK-10",
            nama_mapel="Matematika",
            pengajar=self.user,
        )

        # 3. Siswa Setup
        self.siswa1 = Siswa.objects.create(
            nisn="1234567890",
            nama="Siswa Risk High",
            gender=Siswa.GenderChoices.LAKI_LAKI,
            kelas=self.kelas_a,
        )
        self.siswa2 = Siswa.objects.create(
            nisn="0987654321",
            nama="Siswa Aman",
            gender=Siswa.GenderChoices.PEREMPUAN,
            kelas=self.kelas_a,
        )

        # 4. Presensi Setup (Membuat 2 entri per siswa: 1 Hadir, 1 Alpa = Rata-rata 50%)
        # Siswa 1
        PresensiSiswa.objects.create(
            siswa=self.siswa1,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=1,
            tanggal=datetime.date(2026, 1, 5),
            status=PresensiSiswa.StatusChoices.HADIR,
        )
        PresensiSiswa.objects.create(
            siswa=self.siswa1,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=2,
            tanggal=datetime.date(2026, 1, 12),
            status=PresensiSiswa.StatusChoices.ALPA,
        )

        # Siswa 2
        PresensiSiswa.objects.create(
            siswa=self.siswa2,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=1,
            tanggal=datetime.date(2026, 1, 5),
            status=PresensiSiswa.StatusChoices.HADIR,
        )
        PresensiSiswa.objects.create(
            siswa=self.siswa2,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=2,
            tanggal=datetime.date(2026, 1, 12),
            status=PresensiSiswa.StatusChoices.ALPA,
        )

        # 5. PredictionResult Setup
        self.prediction1 = PredictionResult.objects.create(
            siswa=self.siswa1,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=1,
            risk_score=PredictionResult.RiskChoices.HIGH,
            recommendation="Perlu intervensi intensif",
        )
        self.prediction2 = PredictionResult.objects.create(
            siswa=self.siswa2,
            mapel=self.mapel_math,
            semester=self.semester,
            minggu_ke=1,
            risk_score=PredictionResult.RiskChoices.LOW,
            recommendation="Performa baik",
        )

    def test_get_dashboard_summary_success(self):
        result = get_dashboard_summary()

        self.assertIn("summary", result)
        self.assertIn("trend_performa", result)
        self.assertIn("proporsi_risiko", result)
        self.assertIn("insight_kelas", result)
        self.assertIn("top_intervensi", result)

        self.assertEqual(result["summary"]["total_siswa"], 2)
        self.assertEqual(result["summary"]["risiko_tinggi"], 1)
        self.assertEqual(result["summary"]["risiko_sedang"], 0)
        self.assertEqual(result["summary"]["rata_rata_presensi"], 50.0)

        self.assertEqual(len(result["top_intervensi"]), 1)
        self.assertEqual(result["top_intervensi"][0]["nisn"], self.siswa1.nisn)

    def test_get_dashboard_summary_empty_database(self):
        Siswa.objects.all().delete()
        PredictionResult.objects.all().delete()
        PresensiSiswa.objects.all().delete()
        NilaiSiswa.objects.all().delete()

        result = get_dashboard_summary()

        self.assertEqual(result["summary"]["total_siswa"], 0)
        self.assertEqual(result["summary"]["rata_rata_presensi"], 0.0)
        self.assertEqual(result["proporsi_risiko"]["tinggi"]["percentage"], 0.0)
        self.assertEqual(len(result["top_intervensi"]), 0)

    def test_get_school_analytics_with_filtering(self):
        analytics = get_school_analytics(
            kelas_id=self.kelas_a.id, mapel_id=self.mapel_math.id
        )

        self.assertIn("filter_options", analytics)
        self.assertIn("perbandingan_risiko_kelas", analytics)
        self.assertIn("faktor_utama_risiko", analytics)

        perbandingan = analytics["perbandingan_risiko_kelas"]
        self.assertEqual(len(perbandingan), 1)
        self.assertEqual(perbandingan[0]["nama_kelas"], "X IPA 1")
        self.assertEqual(perbandingan[0]["jumlah_high_risk"], 1)

    def test_selector_query_efficiency(self):
        with self.assertNumQueries(16):
            get_dashboard_summary()