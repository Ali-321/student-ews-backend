from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment import services
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


class AssessmentServicesTest(TestCase):
    def setUp(self):
        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.semester = Semester.objects.create(tahun_ajaran=self.ta, semester_ke=1, is_aktif=True)
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(nisn="0012345678", nama="Budi", gender="L", angkatan=2025, kelas=self.kelas)
        self.mapel = MataPelajaran.objects.create(kode_mapel="MAT10", nama_mapel="Matematika")

    def test_record_studytime_creates_and_updates(self):
        studytime = services.record_studytime(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=1,
            studytime=5
        )
        self.assertEqual(HistoriStudytime.objects.count(), 1)
        self.assertEqual(studytime.studytime, 5)

        # Test update via unique constraint upsert
        updated = services.record_studytime(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=1,
            studytime=8
        )
        self.assertEqual(HistoriStudytime.objects.count(), 1)
        self.assertEqual(updated.studytime, 8)

    def test_create_nilai_siswa_success_and_validation_error(self):
        nilai = services.create_nilai_siswa(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=2,
            jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ,
            nama_evaluasi="Quiz 1",
            skor=85.5
        )
        self.assertEqual(nilai.skor, 85.5)

        with self.assertRaises(ValidationError):
            services.create_nilai_siswa(
                siswa_nisn=self.siswa.nisn,
                mapel_id=self.mapel.id,
                semester_id=self.semester.id,
                minggu_ke=2,
                jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ,
                nama_evaluasi="Quiz Invalid",
                skor=105.0
            )

    def test_bulk_record_presensi(self):
        items = [{"siswa_nisn": self.siswa.nisn, "status": PresensiSiswa.StatusChoices.HADIR}]
        records = services.bulk_record_presensi(
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=1,
            tanggal=date.today(),
            items=items
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, PresensiSiswa.StatusChoices.HADIR)

    def test_record_prediction_result(self):
        pred = services.record_prediction_result(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=4,
            risk_score=PredictionResult.RiskChoices.HIGH,
            recommendation="Perlu pendampingan belajar khusus"
        )
        self.assertEqual(pred.risk_score, PredictionResult.RiskChoices.HIGH)