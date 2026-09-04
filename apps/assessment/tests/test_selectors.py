from datetime import date
from django.test import TestCase

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment import selectors
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


class AssessmentSelectorsTest(TestCase):
    def setUp(self):
        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.semester = Semester.objects.create(tahun_ajaran=self.ta, semester_ke=1, is_aktif=True)
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(nisn="0012345678", nama="Budi", gender="L", kelas=self.kelas)
        self.mapel = MataPelajaran.objects.create(kode_mapel="MAT10", nama_mapel="Matematika")

        NilaiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ,
            nama_evaluasi="Quiz 1", skor=80.0
        )
        NilaiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS,
            nama_evaluasi="Tugas 1", skor=90.0
        )

        PresensiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=1, tanggal=date(2026, 8, 1), status=PresensiSiswa.StatusChoices.HADIR
        )
        PresensiSiswa.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, tanggal=date(2026, 8, 8), status=PresensiSiswa.StatusChoices.ALPA
        )

        PredictionResult.objects.create(
            siswa=self.siswa, mapel=self.mapel, semester=self.semester,
            minggu_ke=2, risk_score=PredictionResult.RiskChoices.HIGH,
            recommendation="Risiko Tinggi"
        )

    def test_nilai_siswa_list_filtering(self):
        qs = selectors.nilai_siswa_list(filters={"siswa_nisn": self.siswa.nisn, "jenis_evaluasi": "QUIZ"})
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().skor, 80.0)

    def test_get_ringkasan_akademik_siswa(self):
        ringkasan = selectors.get_ringkasan_akademik_siswa(
            siswa_nisn=self.siswa.nisn, semester_id=self.semester.id
        )
        self.assertEqual(ringkasan["rata_rata_nilai"], 85.0)
        self.assertEqual(ringkasan["persentase_kehadiran"], 50.0)
        self.assertEqual(ringkasan["total_mapel_berisiko_tinggi"], 1)