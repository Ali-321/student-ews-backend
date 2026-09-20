from datetime import date
from django.test import TestCase

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment import selectors
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


class AssessmentSelectorsTest(TestCase):
    def setUp(self):
        # 1. Setup Academic Domain
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

        # 2. Setup Assessment Data (Minggu 1)
        HistoriStudytime.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, studytime=4
        )
        NilaiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ,
            nama_evaluasi="Quiz 1", skor=80.0
        )
        PresensiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, tanggal=date(2026, 8, 1), status=PresensiSiswa.StatusChoices.HADIR
        )
        PredictionResult.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, risk_score=PredictionResult.RiskChoices.LOW,
            recommendation={"guru": "Pertahankan."}
        )

        # 3. Setup Assessment Data (Minggu 2) - Budi mulai bermasalah
        HistoriStudytime.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, studytime=1
        )
        NilaiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS,
            nama_evaluasi="Tugas 1", skor=90.0
        )
        PresensiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, tanggal=date(2026, 8, 8), status=PresensiSiswa.StatusChoices.ALPA
        )
        PredictionResult.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, risk_score=PredictionResult.RiskChoices.HIGH,
            recommendation={"guru": "Perlu intervensi karena alpa."}
        )

    def test_histori_studytime_list_filtering(self):
        qs = selectors.histori_studytime_list(filters={"minggu_ke": 1})
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().studytime, 4)

    def test_nilai_siswa_list_filtering(self):
        qs = selectors.nilai_siswa_list(filters={"siswa_nisn": self.siswa.nisn, "jenis_evaluasi": "QUIZ"})
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().skor, 80.0)

    def test_presensi_siswa_list_filtering(self):
        qs = selectors.presensi_siswa_list(filters={"status": PresensiSiswa.StatusChoices.ALPA})
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().minggu_ke, 2)

    def test_prediction_result_list_filtering(self):
        qs = selectors.prediction_result_list(filters={"risk_score": PredictionResult.RiskChoices.HIGH})
        self.assertEqual(qs.count(), 1)

    def test_get_presensi_status_choices(self):
        choices = selectors.get_presensi_status_choices()
        self.assertEqual(len(choices), 4)
        self.assertTrue(any(c["value"] == "Hadir" for c in choices))

    def test_get_ringkasan_akademik_siswa(self):
        # Rata-rata dari 80 dan 90 adalah 85.
        # Presensi: 1 Hadir, 1 Alpa -> Kehadiran 50%
        # Risiko tinggi di minggu ke-2
        ringkasan = selectors.get_ringkasan_akademik_siswa(
            siswa_nisn=self.siswa.nisn, semester_id=self.semester.id
        )
        self.assertEqual(ringkasan["rata_rata_nilai"], 85.0)
        self.assertEqual(ringkasan["persentase_kehadiran"], 50.0)
        self.assertEqual(ringkasan["total_mapel_berisiko_tinggi"], 1)

    def test_get_siswa_risk_summary_qs(self):
        # Filter by Kelas
        qs_kelas = selectors.get_siswa_risk_summary_qs(kelas_id=self.kelas.id)
        self.assertEqual(qs_kelas.count(), 1)
        
        # Filter by Pencarian Nama
        qs_search = selectors.get_siswa_risk_summary_qs(search="Budi")
        self.assertEqual(qs_search.count(), 1)

        # Filter by Status Risiko (Minggu terbaru/Minggu 2 adalah HIGH)
        qs_risk = selectors.get_siswa_risk_summary_qs(risk_status="HIGH")
        self.assertEqual(qs_risk.count(), 1)

    def test_attach_metrics_to_paginated_siswa(self):
        siswa_list = list(Siswa.objects.filter(nisn=self.siswa.nisn))
        result = selectors.attach_metrics_to_paginated_siswa(siswa_list)
        
        s = result[0]
        # Atribut virtual harus terpasang (Berdasarkan agregat akumulatif)
        self.assertEqual(s.calc_nilai, 85.0)
        self.assertEqual(s.calc_presensi, "50.0%")
        self.assertEqual(s.calc_risk, "HIGH")

    def test_get_siswa_risk_detail(self):
        # Method ini mengevaluasi kinerja HANYA pada minggu terbaru (Minggu ke-2)
        detail = selectors.get_siswa_risk_detail(nisn=self.siswa.nisn, mapel_id=self.mapel.id)
        
        self.assertEqual(detail["profil_siswa"]["nama_siswa"], "Budi")
        
        # Di minggu ke 2: Presensi Alpa (0% hadir), Tugas (90), Study (1 jam)
        self.assertEqual(detail["metrik_kinerja"]["kehadiran_pct"], 0.0)
        self.assertEqual(detail["metrik_kinerja"]["rata_rata_tugas"], 90.0)
        self.assertEqual(detail["metrik_kinerja"]["study_hour"], 1.0)
        
        self.assertEqual(detail["analisis_ews"]["status_risiko"], "HIGH")
        self.assertEqual(detail["analisis_ews"]["rekomendasi_tindakan"], "Perlu intervensi karena alpa.")